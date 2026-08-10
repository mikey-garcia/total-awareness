import {getPushKey, savePushSubscription} from './http.js';

function decodeKey(value) {
  const padding = '='.repeat((4 - value.length % 4) % 4);
  const raw = atob((value + padding).replace(/-/g, '+').replace(/_/g, '/'));
  return Uint8Array.from([...raw].map(c => c.charCodeAt(0)));
}

export async function enablePush() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    throw new Error('Web Push is not supported here');
  }
  const permission = await Notification.requestPermission();
  if (permission !== 'granted') throw new Error(`notification permission: ${permission}`);

  const registration = await navigator.serviceWorker.register('/service-worker.js');
  const {public_key: publicKey} = await getPushKey();
  if (!publicKey) throw new Error('server has no VAPID public key configured');

  let subscription = await registration.pushManager.getSubscription();
  if (!subscription) {
    subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: decodeKey(publicKey),
    });
  }
  await savePushSubscription(subscription.toJSON());
  return subscription;
}
