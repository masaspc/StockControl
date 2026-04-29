import { api } from "@/lib/api";
import type { Role, UserMe } from "@/types/api";

export async function login(ad_account: string, password: string) {
  return api.post<{ access_token: string; expires_in: number }>(
    "/auth/login",
    { ad_account, password },
  );
}

export async function logout() {
  return api.post<{ message: string }>("/auth/logout");
}

export async function fetchMe(): Promise<UserMe | null> {
  try {
    return await api.get<UserMe>("/auth/me");
  } catch {
    return null;
  }
}

const ROLE_RANK: Record<Role, number> = {
  viewer: 0,
  operator: 1,
  manager: 2,
  admin: 3,
};

export function hasMinRole(user: UserMe | null, min: Role): boolean {
  if (!user) return false;
  return ROLE_RANK[user.role] >= ROLE_RANK[min];
}
