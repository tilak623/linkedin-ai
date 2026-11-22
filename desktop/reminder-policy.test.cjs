const test = require('node:test');
const assert = require('node:assert/strict');
const { shouldSendReminder } = require('./reminder-policy.cjs');

const activeState = {
  authenticated: true,
  remindersEnabled: true,
  interviewCompleted: false,
  intervalMins: 15,
};

test('reminders require an authenticated user, enabled setting, and unfinished interview', () => {
  assert.equal(shouldSendReminder(null, 0, 1_000_000), false);
  assert.equal(shouldSendReminder({ ...activeState, authenticated: false }, 0, 1_000_000), false);
  assert.equal(shouldSendReminder({ ...activeState, remindersEnabled: false }, 0, 1_000_000), false);
  assert.equal(shouldSendReminder({ ...activeState, interviewCompleted: true }, 0, 1_000_000), false);
});

test('reminders follow the configured interval', () => {
  const lastReminderAt = 1_000_000;
  assert.equal(shouldSendReminder(activeState, 0, lastReminderAt), true);
  assert.equal(shouldSendReminder(activeState, lastReminderAt, lastReminderAt + 14 * 60_000), false);
  assert.equal(shouldSendReminder(activeState, lastReminderAt, lastReminderAt + 15 * 60_000), true);
});

test('unsupported saved intervals fail explicitly', () => {
  assert.throws(
    () => shouldSendReminder({ ...activeState, intervalMins: 10 }, 0, 1_000_000),
    /reminder interval is invalid/,
  );
});
