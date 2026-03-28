/**
 * Format a number as currency (EUR by default).
 */
export function formatCurrency(
  amount: number,
  currency = "EUR",
  locale = "en-IE"
): string {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(amount);
}

/**
 * Format an ISO date string to a readable date.
 */
export function formatDate(
  isoDate: string,
  locale = "en-IE",
  options?: Intl.DateTimeFormatOptions
): string {
  const defaults: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
  };
  return new Date(isoDate).toLocaleDateString(locale, options ?? defaults);
}

/**
 * Format hours with one decimal place.
 */
export function formatHours(hours: number): string {
  return `${hours.toFixed(1)}h`;
}

/**
 * Get a display name from first + last name.
 */
export function formatFullName(firstName: string, lastName: string): string {
  return `${firstName} ${lastName}`.trim();
}
