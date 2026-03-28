import { Clock } from "lucide-react";

// TODO: Redirect based on auth state and role once auth is wired up
export default function Home() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4">
      <Clock className="h-12 w-12 text-muted-foreground" />
      <h1 className="text-2xl font-semibold">Welcome to TimeHit</h1>
      <p className="text-muted-foreground">
        Contractor timesheet and invoicing platform
      </p>
    </div>
  );
}
