const SUPPORTED_INTERVALS = [15, 30, 60];

function shouldSendReminder(state, lastReminderAt, now) {
  if (!state || !state.authenticated || !state.remindersEnabled || state.interviewCompleted) {
    return false;
  }
  if (!SUPPORTED_INTERVALS.includes(state.intervalMins)) {
    throw new Error('The saved interview reminder interval is invalid.');
  }
  return !lastReminderAt || now - lastReminderAt >= state.intervalMins * 60_000;
}

module.exports = { shouldSendReminder };
