import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

interface ScoreChartProps {
    score: number;
}

export const ScoreChart: React.FC<ScoreChartProps> = ({ score }) => {
    // Typical credit score range: 300 - 850
    const min = 150;
    const max = 950;
    const value = Math.max(min, Math.min(max, score));

    const data = [
        { value: value - min, color: '#0df26c' }, // Reusing the green from previous conversations if applicable or standard primary
        { value: max - value, color: '#e2e8f0' }
    ];

    const getScoreLabel = (s: number) => {
        if (s < 500) return 'Poor';
        if (s < 650) return 'Fair';
        if (s < 750) return 'Good';
        return 'Excellent';
    };

    return (
        <Card className="h-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase">Credit Score</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center">
                <div className="h-[200px] w-full relative">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="80%"
                                startAngle={180}
                                endAngle={0}
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={0}
                                dataKey="value"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                        </PieChart>
                    </ResponsiveContainer>
                    <div className="absolute inset-x-0 bottom-[20%] flex flex-col items-center justify-center">
                        <span className="text-4xl font-bold">{score}</span>
                        <span className="text-sm font-medium text-muted-foreground uppercase">{getScoreLabel(score)}</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};
