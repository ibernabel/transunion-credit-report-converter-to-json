import React from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import type { AccountDetail } from '@/types/api';
import { cn } from '@/lib/utils';

interface AccountsTableProps {
    accounts: AccountDetail[];
}

export const AccountsTable: React.FC<AccountsTableProps> = ({ accounts }) => {
    return (
        <div className="rounded-md border bg-card">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Bank / Provider</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Balance</TableHead>
                        <TableHead className="text-right">Limit</TableHead>
                        <TableHead>Last Update</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {accounts.map((account, i) => {
                        const isArrears = account.status.toLowerCase().includes('atraso') || account.balance_in_arrears > 0;

                        return (
                            <TableRow key={i}>
                                <TableCell className="font-medium">{account.subscriber}</TableCell>
                                <TableCell>{account.account_type}</TableCell>
                                <TableCell>
                                    <Badge
                                        variant={isArrears ? "destructive" : "secondary"}
                                        className={cn(isArrears ? "bg-red-500 hover:bg-red-600" : "bg-green-500/10 text-green-600 border-green-200")}
                                    >
                                        {account.status}
                                    </Badge>
                                </TableCell>
                                <TableCell className="text-right">
                                    {account.currency} {account.current_balance.toLocaleString()}
                                </TableCell>
                                <TableCell className="text-right">
                                    {account.currency} {account.credit_limit.toLocaleString()}
                                </TableCell>
                                <TableCell className="text-muted-foreground text-sm">
                                    {account.update_date}
                                </TableCell>
                            </TableRow>
                        );
                    })}
                </TableBody>
            </Table>
        </div>
    );
};
