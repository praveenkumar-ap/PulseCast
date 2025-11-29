"use client";

import React from "react";
import { Table, TableCell, TableRow } from "@/components/ui/Table";
import type { ScenarioLedgerEntry } from "@/types/domain";

type Props = {
  entries: ScenarioLedgerEntry[];
};

export function ScenarioLedger({ entries }: Props) {
  if (!entries.length) {
    return <p className="text-sm text-muted">No ledger events yet.</p>;
  }

  return (
    <Table headers={["Seq", "Action", "Actor", "Comments", "Created at"]}>
      {entries.map((e) => (
        <TableRow key={e.ledgerId}>
          <TableCell>{e.versionSeq}</TableCell>
          <TableCell>{e.actionType}</TableCell>
          <TableCell>{e.actor}</TableCell>
          <TableCell>{e.comments || "—"}</TableCell>
          <TableCell>{new Date(e.createdAt).toLocaleString()}</TableCell>
        </TableRow>
      ))}
    </Table>
  );
}
