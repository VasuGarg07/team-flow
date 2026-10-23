import { useParams } from "react-router-dom";

export function useNumericParam(name: string): number {
  const params = useParams();
  return Number(params[name]);
}
