import React from 'react';
import { Calendar as CalendarIcon, Clock, CheckCircle2, AlertCircle } from 'lucide-react';

export const Calendar: React.FC = () => {
  const scheduleItems = [
    {
      date: 'Today, Nov 17',
      time: '08:30 AM (Recommended)',
      title: 'Architecting an Asynchronous Database Layer with Zero External Dependencies',
      status: 'pending_approval',
      reason: 'Peak engagement window for engineering leads in your target timezone.',
    },
    {
      date: 'Tomorrow, Nov 18',
      time: '09:00 AM',
      title: 'Standup Interview Scheduled',
      status: 'scheduled_interview',
      reason: 'Capturing next progress milestone.',
    },
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="p-4 rounded-xl bg-surface-900 border border-surface-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CalendarIcon className="w-5 h-5 text-brand-400" />
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Smart Cadence Manager</h3>
            <p className="text-xs text-slate-400">Adaptive schedule based on genuine activity. Never forces low-quality daily posting.</p>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {scheduleItems.map((item, idx) => (
          <div key={idx} className="p-5 rounded-xl bg-surface-900 border border-surface-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-xs">
                <span className="font-semibold text-brand-400">{item.date}</span>
                <span className="text-slate-500">•</span>
                <span className="text-slate-300 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-slate-400" />
                  <span>{item.time}</span>
                </span>
              </div>
              <div className="text-sm font-bold text-slate-100">{item.title}</div>
              <div className="text-xs text-slate-400">{item.reason}</div>
            </div>

            <span className="px-3 py-1 rounded-full text-xs font-medium self-start md:self-center bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Approval Required
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
