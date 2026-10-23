import { Button } from "@/components/ui/button";
import { ErrorBox } from "@/components/PageState";
import { Modal } from "@/components/ui/modal";

type ConfirmDialogProps = {
  open: boolean;
  title: string;
  message: string;
  confirmLabel: string;
  error: string | null;
  isPending: boolean;
  onConfirm: () => void;
  onClose: () => void;
};

export function ConfirmDialog(props: ConfirmDialogProps) {
  return (
    <Modal open={props.open} title={props.title} onClose={props.onClose}>
      <p className="text-sm text-muted-foreground">{props.message}</p>
      {props.error !== null && <ErrorBox message={props.error} />}
      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={props.onClose}>
          Cancel
        </Button>
        <Button variant="destructive" onClick={props.onConfirm} disabled={props.isPending}>
          {props.isPending ? "Working..." : props.confirmLabel}
        </Button>
      </div>
    </Modal>
  );
}
