import { useDeferredValue, useState } from "react";
import { Search, X } from "lucide-react";

import { SectionCard } from "@/components/common/SectionCard";
import { SeverityBadge } from "@/components/features/alerts/SeverityBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { POLLING_INTERVALS } from "@/config/app";
import {
  CRACK_CLASS_LABELS,
  HISTORY_PAGE_SIZE,
  SEVERITY_LABELS,
  SEVERITY_ORDER,
} from "@/constants/monitoring";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";
import { formatConfidence, formatCoordinate, formatDateTime } from "@/utils/format";
import type { Severity } from "@/types/monitoring";

type SeverityFilter = Severity | "ALL";

export function DetectionHistoryTable() {
  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState<SeverityFilter>("ALL");
  const [page, setPage] = useState(1);
  const deferredSearch = useDeferredValue(search);

  const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(
    ["detections", deferredSearch, severity, page],
    () =>
      monitoringApi.getDetections({
        search: deferredSearch,
        severity,
        page,
        pageSize: HISTORY_PAGE_SIZE,
      }),
    POLLING_INTERVALS.detections,
  );

  const total = data?.total ?? 0;
  const pageCount = Math.max(1, Math.ceil(total / HISTORY_PAGE_SIZE));
  const hasFilters = search.trim() !== "" || severity !== "ALL";

  const resetFilters = () => {
    setSearch("");
    setSeverity("ALL");
    setPage(1);
  };

  return (
    <SectionCard
      title="Detection History"
      description={`${total} record${total === 1 ? "" : "s"}`}
      className="h-full"
      loading={isPending}
      error={isError}
      onRetry={refetch}
      updatedAt={dataUpdatedAt}
      contentClassName="flex flex-col gap-4"
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden
          />
          <Input
            value={search}
            onChange={(event) => {
              setSearch(event.target.value);
              setPage(1);
            }}
            placeholder="Search by ID or class…"
            aria-label="Search detections"
            className="pl-9"
          />
        </div>
        <div className="flex items-center gap-2">
          <Select
            value={severity}
            onValueChange={(value) => {
              setSeverity(value as SeverityFilter);
              setPage(1);
            }}
          >
            <SelectTrigger className="w-full sm:w-44" aria-label="Filter by severity">
              <SelectValue placeholder="Severity" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">All severities</SelectItem>
              {SEVERITY_ORDER.map((item) => (
                <SelectItem key={item} value={item}>
                  {SEVERITY_LABELS[item]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {hasFilters && (
            <Button
              type="button"
              size="sm"
              variant="ghost"
              onClick={resetFilters}
              aria-label="Clear filters"
            >
              <X className="size-4" aria-hidden />
              Clear
            </Button>
          )}
        </div>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Time</TableHead>
            <TableHead>Class</TableHead>
            <TableHead>Severity</TableHead>
            <TableHead className="text-right">Confidence</TableHead>
            <TableHead className="hidden md:table-cell">Location</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {(data?.items ?? []).map((detection) => (
            <TableRow key={detection.id}>
              <TableCell className="whitespace-nowrap text-muted-foreground">
                {formatDateTime(detection.timestamp)}
              </TableCell>
              <TableCell className="whitespace-nowrap">
                {CRACK_CLASS_LABELS[detection.crackClass]}
              </TableCell>
              <TableCell>
                <SeverityBadge severity={detection.severity} />
              </TableCell>
              <TableCell className="text-right tabular-nums">
                {formatConfidence(detection.confidence)}
              </TableCell>
              <TableCell className="hidden whitespace-nowrap font-mono text-xs text-muted-foreground md:table-cell">
                {formatCoordinate(detection.latitude)}, {formatCoordinate(detection.longitude)}
              </TableCell>
            </TableRow>
          ))}
          {data && data.items.length === 0 && (
            <TableRow>
              <TableCell colSpan={5} className="py-8 text-center text-muted-foreground">
                {hasFilters
                  ? "No detections match the current filters."
                  : "No detections recorded yet."}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <span className="text-xs text-muted-foreground">
          Page {page} of {pageCount}
        </span>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            disabled={page <= 1}
            onClick={() => setPage((current) => Math.max(1, current - 1))}
          >
            Previous
          </Button>
          <Button
            size="sm"
            variant="outline"
            disabled={page >= pageCount}
            onClick={() => setPage((current) => Math.min(pageCount, current + 1))}
          >
            Next
          </Button>
        </div>
      </div>
    </SectionCard>
  );
}
