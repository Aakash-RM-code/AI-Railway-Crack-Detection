import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowDown, ArrowUp, OctagonX, Square } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { LabeledValue } from "@/components/common/LabeledValue";
import { SectionCard } from "@/components/common/SectionCard";
import { StatusDot } from "@/components/common/StatusDot";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { POLLING_INTERVALS } from "@/config/app";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";
import type { RoverCommand } from "@/types/monitoring";

// The rover firmware moves forward/backward and stops; there are no steering
// commands, so the D-pad only exposes supported directions.
const PAD: Array<{ command: RoverCommand; icon: LucideIcon; label: string; cell: string }> = [
  { command: "forward", icon: ArrowUp, label: "Forward", cell: "col-start-2 row-start-1" },
  { command: "stop", icon: Square, label: "Stop", cell: "col-start-2 row-start-2" },
  { command: "backward", icon: ArrowDown, label: "Backward", cell: "col-start-2 row-start-3" },
];

const SPEED_MAX = 255;

export function RoverControlCard() {
  const queryClient = useQueryClient();
  const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(
    ["rover"],
    () => monitoringApi.getRoverState(),
    POLLING_INTERVALS.rover,
    undefined,
    "telemetry",
  );

  const send = useMutation({
    mutationFn: (payload: { command: RoverCommand; speed?: number }) =>
      monitoringApi.sendRoverCommand(payload),
    onSuccess: (state) => queryClient.setQueryData(["rover"], state),
  });

  const speed = data?.speed ?? 0;
  const stopped = data?.emergencyStopped ?? false;
  const disabled = send.isPending || data?.state !== "connected";

  return (
    <SectionCard
      title="Rover Control"
      className="h-full"
      loading={isPending}
      error={isError}
      onRetry={refetch}
      updatedAt={dataUpdatedAt}
      actions={<StatusDot state={data?.state ?? "disconnected"} />}
      contentClassName="flex flex-col gap-5"
    >
      <div className="mx-auto grid w-full max-w-[13rem] grid-cols-3 grid-rows-3 gap-2">
        {PAD.map(({ command, icon: Icon, label, cell }) => (
          <Button
            key={command}
            variant={command === "stop" ? "secondary" : "outline"}
            size="icon"
            aria-label={label}
            className={`${cell} size-full aspect-square`}
            disabled={disabled || (stopped && command !== "stop")}
            onClick={() => send.mutate({ command })}
          >
            <Icon className="size-4" aria-hidden />
          </Button>
        ))}
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs uppercase tracking-wide text-muted-foreground">Speed</span>
          <span className="text-sm font-medium text-foreground">
            {speed} / {SPEED_MAX}
          </span>
        </div>
        <Slider
          value={[speed]}
          min={0}
          max={SPEED_MAX}
          step={5}
          aria-label="Rover speed"
          disabled={disabled}
          // Set speed without issuing a movement command (no "stop" spam).
          onValueCommit={(values) => send.mutate({ command: "set_speed", speed: values[0] ?? 0 })}
        />
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <LabeledValue
          label="Last command"
          value={data?.lastCommand ? data.lastCommand.replace("_", " ") : "—"}
        />
        <Button
          variant="destructive"
          size="sm"
          disabled={send.isPending}
          onClick={() => send.mutate({ command: stopped ? "stop" : "emergency_stop" })}
        >
          <OctagonX className="size-4" aria-hidden />
          {stopped ? "Release" : "E-Stop"}
        </Button>
      </div>
    </SectionCard>
  );
}
