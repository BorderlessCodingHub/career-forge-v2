/** Open a fresh Customer Portal session. This click is not Roadmap presence. */
export async function redirectToCardUpdate(
  startPortal: () => Promise<string>,
  assign: (url: string) => void,
): Promise<void> {
  const url = await startPortal();
  assign(url);
}
