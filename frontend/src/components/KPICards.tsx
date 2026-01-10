import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CreditCard, Landmark, TrendingUp } from 'lucide-react';

interface KPICardsProps {
    totalDebt: number;
    utilization: number;
    openAccounts: number;
}

export const KPICards: React.FC<KPICardsProps> = ({ totalDebt, utilization, openAccounts }) => {
    const cards = [
        {
            title: 'Total Debt',
            value: `$${totalDebt.toLocaleString(undefined, { minimumFractionDigits: 2 })}`,
            icon: Landmark,
            description: 'Total current balance across all accounts'
        },
        {
            title: 'Utilization',
            value: `${utilization.toFixed(1)}%`,
            icon: CreditCard,
            description: 'Percentage of available credit in use'
        },
        {
            title: 'Open Accounts',
            value: openAccounts.toString(),
            icon: TrendingUp,
            description: 'Number of active credit accounts'
        }
    ];

    return (
        <div className="grid gap-4 md:grid-cols-3">
            {cards.map((card, i) => (
                <Card key={i}>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
                        <card.icon className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{card.value}</div>
                        <p className="text-xs text-muted-foreground mt-1">
                            {card.description}
                        </p>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
};
