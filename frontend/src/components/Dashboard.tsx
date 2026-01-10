import React from 'react';
import type { CreditReport } from '@/types/api';
import { ScoreChart } from './ScoreChart';
import { KPICards } from './KPICards';
import { AccountsTable } from './AccountsTable';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { User, MapPin, Calendar, Hash } from 'lucide-react';

interface DashboardProps {
    report: CreditReport;
}

export const Dashboard: React.FC<DashboardProps> = ({ report }) => {
    const { personal_data, score, details_open_accounts } = report;

    // Calculate KPIs
    const totalDebt = details_open_accounts.reduce((sum, acc) => sum + acc.current_balance, 0);
    const totalLimit = details_open_accounts.reduce((sum, acc) => sum + acc.credit_limit, 0);
    const utilization = totalLimit > 0 ? (totalDebt / totalLimit) * 100 : 0;
    const openAccountsCount = details_open_accounts.length;

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Header Info */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card className="md:col-span-2">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <User className="h-5 w-5 text-primary" />
                            {personal_data.nombres} {personal_data.apellidos}
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div className="flex items-center gap-2 text-muted-foreground">
                                <Hash className="h-4 w-4" />
                                <span>ID: {personal_data.cedula}</span>
                            </div>
                            <div className="flex items-center gap-2 text-muted-foreground">
                                <Calendar className="h-4 w-4" />
                                <span>Born: {personal_data.fecha_nacimiento}</span>
                            </div>
                            <div className="flex items-center gap-2 text-muted-foreground col-span-2">
                                <MapPin className="h-4 w-4" />
                                <span className="truncate">{personal_data.direcciones[0] || 'No address provided'}</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {score && <ScoreChart score={score.score || 0} />}
            </div>

            {/* KPIs */}
            <KPICards
                totalDebt={totalDebt}
                utilization={utilization}
                openAccounts={openAccountsCount}
            />

            {/* Accounts Table */}
            <div className="space-y-2">
                <h3 className="text-lg font-semibold px-1">Detailed Open Accounts</h3>
                <AccountsTable accounts={details_open_accounts} />
            </div>
        </div>
    );
};
