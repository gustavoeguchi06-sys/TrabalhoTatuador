/* Notificações push: registra o service worker, pede permissão uma vez
   e envia a inscrição para o servidor. */
(function () {
  const btn = document.getElementById('btnNotify');
  const label = document.getElementById('btnNotifyLabel');
  if (!btn) return;

  const supported = 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
  if (!supported) {
    btn.style.display = 'none';
    return;
  }

  function setOn() {
    btn.classList.add('on');
    btn.title = 'Lembretes ativados';
    if (label) label.textContent = 'Lembretes ativos';
  }

  function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const raw = atob(base64);
    const output = new Uint8Array(raw.length);
    for (let i = 0; i < raw.length; i++) output[i] = raw.charCodeAt(i);
    return output;
  }

  async function getRegistration() {
    return navigator.serviceWorker.register('/sw.js');
  }

  async function sendSubscription(subscription, isNew) {
    await fetch('/push/subscribe/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.CSRF_TOKEN },
      body: JSON.stringify(subscription.toJSON()),
    });
    if (isNew) {
      await fetch('/push/test/', {
        method: 'POST',
        headers: { 'X-CSRFToken': window.CSRF_TOKEN },
      });
    }
  }

  async function subscribe() {
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
      alert('Para receber os lembretes, permita as notificações do navegador.');
      return;
    }
    const reg = await getRegistration();
    let sub = await reg.pushManager.getSubscription();
    const isNew = !sub;
    if (!sub) {
      const resp = await fetch('/push/vapid/');
      const { publicKey } = await resp.json();
      sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(publicKey),
      });
    }
    await sendSubscription(sub, isNew);
    setOn();
  }

  btn.addEventListener('click', function () {
    subscribe().catch(function (err) {
      console.error('Falha ao ativar notificações:', err);
      alert('Não foi possível ativar as notificações. Tente novamente.');
    });
  });

  // Se já está inscrito, apenas mostra o estado e mantém o servidor atualizado.
  if (Notification.permission === 'granted') {
    navigator.serviceWorker.getRegistration('/sw.js').then(async function (reg) {
      if (!reg) return;
      const sub = await reg.pushManager.getSubscription();
      if (sub) {
        setOn();
        sendSubscription(sub, false).catch(function () {});
      }
    });
  }
})();
