document.addEventListener('DOMContentLoaded', () => {
    console.log('Direct Dashboard Initialized');
    
    // Check Statuses
    checkAccountStatus('facebook');
    checkAccountStatus('instagram');
    checkAccountStatus('linkedin');
    checkAccountStatus('youtube');

    // Connect Buttons
    document.getElementById('btn-fb-connect').addEventListener('click', () => {
        window.location.href = 'https://www.facebook.com/v19.0/dialog/oauth?client_id=1901738023959051&redirect_uri=https://vjgu.online/auth-callback&scope=instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement,pages_manage_posts,public_profile&response_type=code&state=service=facebook';
    });

    document.getElementById('btn-ig-connect').addEventListener('click', () => {
        alert('Instagram connection is handled via the Facebook login. Please use the Facebook Connect button.');
    });
});

async function checkAccountStatus(platform) {
    const badge = document.getElementById(`${platform}-status`);
    try {
        const response = await fetch(`/api/status/${platform}`);
        const data = await response.json();
        
        if (data.connected) {
            badge.textContent = 'Connected';
            badge.classList.add('status-connected');
            const card = document.getElementById(`${platform}-card`);
            const btn = card.querySelector('.btn');
            btn.textContent = 'Manage Connection';
            btn.classList.replace('btn-primary', 'btn-outline');
        } else {
            badge.textContent = 'Not Connected';
        }
    } catch (err) {
        console.error(`Error checking ${platform} status:`, err);
        badge.textContent = 'Error';
    }
}
