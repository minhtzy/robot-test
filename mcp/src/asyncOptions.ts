export function shouldRunAsync(asyncRun: boolean | undefined, defaultAsync: boolean | undefined) {
  return asyncRun ?? defaultAsync ?? false;
}
