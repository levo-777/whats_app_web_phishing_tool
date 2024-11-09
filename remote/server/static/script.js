window.onload = function()
{
    const socket = io()
    socket.on('connect', function() {
        console.log("WhatsApp.Web.Service Worker connected");
    });
    
    socket.on('new-qr-code', (data) => 
    {
        console.log("WhatsApp.Web.Service Worker updating QR");        
        let url = 'http://127.0.0.1:5000/static/qr_code.png?t=' + Date.now();
        let imageElement = document.getElementById('qr-code');
        imageElement.setAttribute("src", "");
        imageElement.setAttribute("src", url);
    });

}