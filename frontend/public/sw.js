self.addEventListener('push',e=>{const d=e.data?e.data.json():{};e.waitUntil(self.registration.showNotification(d.title||'GrantsAssistant',{body:d.body||''}));});
self.addEventListener('notificationclick',e=>{e.notification.close();e.waitUntil(clients.openWindow('/'));});
