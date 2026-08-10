async function request(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  const text = await response.text();
  return text ? JSON.parse(text) : null;
}

export const getSnapshot = () => request('/api/snapshot');
export const getPushKey = () => request('/api/push/key');
export const savePushSubscription = subscription => request('/api/push/subscribe', {
  method: 'POST', headers: {'content-type': 'application/json'}, body: JSON.stringify(subscription)
});
export const sendTestPush = () => request('/api/push/test', {method: 'POST'});
