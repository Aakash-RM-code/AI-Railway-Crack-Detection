import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { MessageSquare, SignalHigh } from "lucide-react";
import { toast } from "sonner";

import { LabeledValue } from "@/components/common/LabeledValue";
import { SectionCard } from "@/components/common/SectionCard";
import { StatusDot } from "@/components/common/StatusDot";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { POLLING_INTERVALS } from "@/config/app";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";
import { formatTime } from "@/utils/format";

export function GsmCard() {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [message, setMessage] = useState("");

  const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(
    ["gsm"],
    () => monitoringApi.getGsmStatus(),
    POLLING_INTERVALS.gsm,
    undefined,
    "telemetry",
  );

  const sendSms = useMutation({
    mutationFn: () => monitoringApi.sendSms({ phoneNumber, message }),
    onSuccess: (result) => {
      if (result.ok) {
        toast.success(result.message);
        setMessage("");
      } else {
        toast.error(result.message);
      }
    },
    onError: () => toast.error("Failed to send SMS"),
  });

  const canSend = phoneNumber.trim().length >= 6 && message.trim().length > 0;

  return (
    <SectionCard
      title="GSM Messaging"
      className="h-full"
      loading={isPending}
      error={isError}
      onRetry={refetch}
      updatedAt={dataUpdatedAt}
      actions={
        <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <StatusDot state={data?.state ?? "disconnected"} />
          <SignalHigh className="size-4" aria-hidden />
          {data?.signalStrength ?? 0}%
        </span>
      }
      contentClassName="flex flex-col gap-4"
    >
      <div className="grid grid-cols-2 gap-4">
        <LabeledValue label="Operator" value={data?.operator ?? "—"} />
        <LabeledValue
          label="Last message"
          value={data?.lastMessageAt ? formatTime(data.lastMessageAt) : "—"}
        />
      </div>

      <form
        className="flex flex-col gap-3"
        onSubmit={(event) => {
          event.preventDefault();
          if (canSend) sendSms.mutate();
        }}
      >
        <Input
          value={phoneNumber}
          onChange={(event) => setPhoneNumber(event.target.value)}
          placeholder="+91 98765 43210"
          aria-label="Recipient phone number"
          inputMode="tel"
        />
        <Textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Alert message…"
          aria-label="SMS message"
          rows={3}
        />
        <Button type="submit" size="sm" disabled={!canSend || sendSms.isPending}>
          <MessageSquare className="size-4" aria-hidden />
          {sendSms.isPending ? "Sending…" : "Send SMS Alert"}
        </Button>
      </form>
    </SectionCard>
  );
}
