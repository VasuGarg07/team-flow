import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { UserMinus, UserPlus, Users } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import type { Member, Role } from "@/api/types";
import {
  useAddMember,
  useChangeMemberRole,
  useMembers,
  useRemoveMember,
  useWorkspace,
} from "@/api/workspaces";
import { useAuth } from "@/auth/AuthContext";
import { Avatar } from "@/components/Avatar";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { EmptyState, ErrorBox, Loading, QueryError } from "@/components/PageState";
import { RoleBadge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { errorMessage, showServerError } from "@/lib/forms";
import { labelFor } from "@/lib/format";
import { useNumericParam } from "@/lib/params";
import { canChangeRoles, canManageWorkspace, canRemoveMember } from "@/lib/permissions";

const addSchema = z.object({
  email: z.email("Enter a valid email"),
  role: z.enum(["ADMIN", "MEMBER"]),
});

type AddValues = z.infer<typeof addSchema>;

function AddMemberForm({ workspaceId, myRole }: { workspaceId: number; myRole: Role }) {
  const addMember = useAddMember(workspaceId);
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors },
  } = useForm<AddValues>({ resolver: zodResolver(addSchema), defaultValues: { email: "", role: "MEMBER" } });

  async function onSubmit(values: AddValues) {
    setServerError(null);
    try {
      await addMember.mutateAsync(values);
      reset();
    } catch (error) {
      setServerError(showServerError(error, setError));
    }
  }

  return (
    <div className="grid gap-2">
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-wrap items-start gap-2" noValidate>
        <div className="grid min-w-56 flex-1 gap-1.5 sm:max-w-xs">
          <Input
            type="email"
            placeholder="Email of a registered user"
            aria-label="Email"
            aria-invalid={errors.email !== undefined}
            {...register("email")}
          />
          {errors.email !== undefined && <span className="text-xs text-destructive">{errors.email.message}</span>}
        </div>
        <Select aria-label="Role" className="w-32" {...register("role")}>
          <option value="MEMBER">Member</option>
          {myRole === "OWNER" && <option value="ADMIN">Admin</option>}
        </Select>
        <Button type="submit" variant="brand" disabled={addMember.isPending}>
          <UserPlus size={16} />
          Add member
        </Button>
      </form>
      {serverError !== null && <ErrorBox message={serverError} />}
    </div>
  );
}

export function MembersPage() {
  const workspaceId = useNumericParam("workspaceId");
  const { user } = useAuth();
  const workspace = useWorkspace(workspaceId);
  const members = useMembers(workspaceId);
  const changeRole = useChangeMemberRole(workspaceId);
  const removeMember = useRemoveMember(workspaceId);
  const [removing, setRemoving] = useState<Member | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const myRole = workspace.data?.role;

  async function onRoleChange(member: Member, role: Role) {
    setActionError(null);
    try {
      await changeRole.mutateAsync({ userId: member.user_id, role });
    } catch (error) {
      setActionError(errorMessage(error));
    }
  }

  async function confirmRemove() {
    if (removing === null) return;
    setActionError(null);
    try {
      await removeMember.mutateAsync(removing.user_id);
      setRemoving(null);
    } catch (error) {
      setActionError(errorMessage(error));
    }
  }

  return (
    <div className="grid gap-4">
      <h2 className="text-lg font-semibold tracking-tight">Members</h2>

      {myRole !== undefined && canManageWorkspace(myRole) && (
        <AddMemberForm workspaceId={workspaceId} myRole={myRole} />
      )}
      {actionError !== null && removing === null && <ErrorBox message={actionError} />}

      {members.isPending && <Loading />}
      {members.isError && <QueryError error={members.error} />}
      {members.data?.length === 0 && <EmptyState icon={Users} title="No members" />}
      {members.data !== undefined && members.data.length > 0 && myRole !== undefined && (
        <ul className="divide-y rounded-lg border bg-card">
          {members.data.map((member) => (
            <li key={member.user_id} className="flex items-center justify-between gap-4 p-4">
              <div className="flex min-w-0 items-center gap-3">
                <Avatar user={member.user} className="h-9 w-9 text-xs" />
                <div className="min-w-0">
                  <p className="font-medium">
                    {member.user.first_name} {member.user.last_name}
                    {member.user_id === user?.id && <span className="ml-2 text-xs text-muted-foreground">You</span>}
                  </p>
                  <p className="truncate text-sm text-muted-foreground">{member.user.email}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {canChangeRoles(myRole) && member.role !== "OWNER" ? (
                  <Select
                    aria-label={`Role for ${member.user.first_name}`}
                    className="w-28"
                    value={member.role}
                    onChange={(event) => onRoleChange(member, event.target.value as Role)}
                  >
                    <option value="ADMIN">{labelFor("ADMIN")}</option>
                    <option value="MEMBER">{labelFor("MEMBER")}</option>
                  </Select>
                ) : (
                  <RoleBadge role={member.role} />
                )}
                {canRemoveMember(myRole, member.role) && (
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Remove member"
                    onClick={() => {
                      setActionError(null);
                      setRemoving(member);
                    }}
                  >
                    <UserMinus size={16} />
                  </Button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      <ConfirmDialog
        open={removing !== null}
        title="Remove member"
        message={`Remove ${removing?.user.first_name ?? ""} ${removing?.user.last_name ?? ""} from this workspace?`}
        confirmLabel="Remove"
        error={actionError}
        isPending={removeMember.isPending}
        onConfirm={confirmRemove}
        onClose={() => setRemoving(null)}
      />
    </div>
  );
}
