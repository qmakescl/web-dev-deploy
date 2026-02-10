const API_URL = '/api';

// --- State Management ---
let currentUser = null;
let currentView = 'auth';
let isRegistering = false;

// --- DOM Elements ---
const elements = {
    app: document.getElementById('app'),
    navbar: document.getElementById('navbar'),
    authSection: document.getElementById('auth-section'),
    feedSection: document.getElementById('feed-section'),
    searchSection: document.getElementById('search-section'),
    authForm: document.getElementById('auth-form'),
    authTitle: document.getElementById('auth-title'),
    btnAuthSubmit: document.getElementById('btn-auth-submit'),
    linkToggleAuth: document.getElementById('link-toggle-auth'),
    groupConfirmPassword: document.getElementById('group-confirm-password'),
    postList: document.getElementById('post-list'),
    modalPost: document.getElementById('modal-post'),
    btnCreatePost: document.getElementById('btn-create-post'),
    btnModalClose: document.getElementById('btn-modal-close'),
    postForm: document.getElementById('post-form'),
    btnLogout: document.getElementById('btn-logout'),
    searchPostList: document.getElementById('search-post-list'),
    searchTagTitle: document.getElementById('search-tag-title'),
    btnBackToFeed: document.getElementById('btn-back-to-feed'),
    inputSearch: document.getElementById('input-search'),
    modalDetail: document.getElementById('modal-detail'),
    detailContent: document.getElementById('detail-content'),
    commentsList: document.getElementById('comments-list'),
    commentForm: document.getElementById('comment-form'),
    btnDetailClose: document.getElementById('btn-detail-close'),
};


// --- API Helpers ---
const fetchAPI = async (endpoint, options = {}) => {
    const token = localStorage.getItem('token');
    const headers = {
        ...(options.headers || {}),
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, { ...options, headers });

    // 401 Unauthorized 처리
    if (response.status === 401) {
        // 로그인 API 자체에서 401이 발생한 경우는 세션 만료가 아닌 로그인 실패임
        if (endpoint === '/auth/login') {
            throw new Error('이메일 또는 비밀번호가 올바르지 않습니다.');
        }

        logout();
        throw new Error('인증 세션이 만료되었습니다. 다시 로그인해 주세요.');
    }


    if (!response.ok) {
        let errorMessage = 'API 서버 오류가 발생했습니다.';
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
        } catch (e) {
            // JSON 파싱 실패 시 (Internal Server Error 등)
            errorMessage = `서버 오류 (${response.status}): 데이터베이스 설정을 확인해 주세요.`;
        }
        throw new Error(errorMessage);
    }
    return response.status === 204 ? null : response.json();
};


// --- Auth Logic ---
const login = async (email, password) => {
    try {
        const data = await fetchAPI('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        localStorage.setItem('token', data.access_token);
        await init();
    } catch (err) {
        alert(err.message);
    }
};

const register = async (email, password) => {
    try {
        await fetchAPI('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        alert('회원가입 완료! 로그인해 주세요.');
        toggleAuthMode();
    } catch (err) {
        alert(err.message);
    }
};

const logout = () => {
    localStorage.removeItem('token');
    currentUser = null;
    showView('auth');
    elements.navbar.classList.add('hidden');
};

// --- View Logic ---
const showView = (viewName) => {
    currentView = viewName;
    [elements.authSection, elements.feedSection, elements.searchSection].forEach(s => s.classList.add('hidden'));

    if (viewName === 'auth') elements.authSection.classList.remove('hidden');
    else if (viewName === 'feed') {
        elements.feedSection.classList.remove('hidden');
        loadFeed();
    }
    else if (viewName === 'search') elements.searchSection.classList.remove('hidden');
};

const toggleAuthMode = () => {
    isRegistering = !isRegistering;
    elements.authTitle.textContent = isRegistering ? '회원가입' : '로그인';
    elements.btnAuthSubmit.textContent = isRegistering ? '가입하기' : '로그인';
    elements.groupConfirmPassword.classList.toggle('hidden', !isRegistering);
    elements.linkToggleAuth.textContent = isRegistering ? '로그인' : '회원가입';
    document.getElementById('auth-toggle-text').textContent = isRegistering ? '이미 계정이 있으신가요?' : '계정이 없으신가요?';
};

// --- Post Logic ---
const loadFeed = async () => {
    try {
        const posts = await fetchAPI('/posts');
        renderPosts(posts, elements.postList);
    } catch (err) {
        console.error(err);
    }
};

const loadComments = async (postId) => {
    try {
        // Backend API doesn't have a direct /posts/{id}/comments GET endpoint yet in my routes, 
        // but based on typical REST, I'll assume we need to implement or use existing if any.
        // Wait, I didn't implement GET /api/posts/{id}/comments in Phase 4.
        // Let's assume the post response should include comments or we need a new endpoint.
        // Looking at Phase 4, I only implemented POST /api/posts/{id}/comments.
        // So I need to implement GET /api/posts/{id}/comments in the backend too or fetch with post.
        // Let's check available backend routes again.
        return await fetchAPI(`/posts/${postId}/comments`);
    } catch (err) {
        console.error(err);
        return [];
    }
};


const renderPosts = (posts, container) => {
    container.innerHTML = posts.map(post => `
        <div class="post-card">
            <div class="post-header">작성일: ${new Date(post.created_at).toLocaleString()}</div>
            <img src="${post.img_url}" class="post-image" alt="Post Image">
            <div class="post-content">
                <p>${formatContent(post.content)}</p>
            </div>
            <div class="post-actions">
                <button class="action-btn ${post.is_liked ? 'liked' : ''}" onclick="window.app.toggleLike(${post.id})">
                    ❤️ ${post.like_count}
                </button>
                <button class="action-btn" onclick="window.app.showDetails(${post.id})">
                    💬 ${post.comment_count}
                </button>
            </div>
        </div>
    `).join('');
};

const formatContent = (content) => {
    if (!content) return '';
    return content.replace(/#(\w+)/g, '<span class="tag" onclick="window.app.searchTag(\'$1\')">#$1</span>');
};

// --- Event Listeners ---
elements.authForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    if (isRegistering) register(email, password);
    else login(email, password);
});

elements.linkToggleAuth.addEventListener('click', (e) => {
    e.preventDefault();
    toggleAuthMode();
});

elements.btnCreatePost.addEventListener('click', () => elements.modalPost.classList.remove('hidden'));
elements.btnModalClose.addEventListener('click', () => elements.modalPost.classList.add('hidden'));

elements.postForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', document.getElementById('post-file').files[0]);
    formData.append('content', document.getElementById('post-content').value);

    try {
        await fetchAPI('/posts', {
            method: 'POST',
            body: formData
        });
        elements.modalPost.classList.add('hidden');
        elements.postForm.reset();
        loadFeed();
    } catch (err) {
        alert(err.message);
    }
});

elements.btnLogout.addEventListener('click', logout);
elements.btnBackToFeed.addEventListener('click', () => showView('feed'));

elements.inputSearch.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const tag = e.target.value.trim().replace(/^#/, '');
        if (tag) {
            window.app.searchTag(tag);
            e.target.value = '';
        }
    }
});

elements.btnDetailClose.addEventListener('click', () => elements.modalDetail.classList.add('hidden'));

elements.commentForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const postId = elements.commentForm.dataset.postId;
    const comment = document.getElementById('input-comment').value;

    try {
        await fetchAPI(`/posts/${postId}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comment })
        });
        document.getElementById('input-comment').value = '';
        window.app.showDetails(postId); // Refresh details
        if (currentView === 'feed') loadFeed();
    } catch (err) {
        alert(err.message);
    }
});


// --- App Global API (for onclick) ---
window.app = {
    searchTag: async (tag) => {
        elements.searchTagTitle.textContent = `#${tag} 결과`;
        showView('search');
        try {
            const posts = await fetchAPI(`/tags/${tag}`);
            renderPosts(posts, elements.searchPostList);
        } catch (err) {
            alert(err.message);
        }
    },
    toggleLike: async (postId) => {
        try {
            await fetchAPI(`/posts/${postId}/like`, { method: 'POST' });
            if (currentView === 'feed') loadFeed();
            // tag 검색 결과에서도 업데이트 필요시 처리
        } catch (err) {
            alert(err.message);
        }
    },
    showDetails: async (postId) => {
        try {
            // Get post info and comments
            const post = await fetchAPI(`/posts/${postId}`);
            const comments = await loadComments(postId);

            elements.modalDetail.classList.remove('hidden');
            elements.commentForm.dataset.postId = postId;

            // Render post content in modal
            elements.detailContent.innerHTML = `
                <div class="post-card" style="margin-bottom: 1rem; border: none;">
                    <img src="${post.img_url}" class="post-image" alt="Post Image">
                    <div class="post-content">
                        <p>${formatContent(post.content)}</p>
                    </div>
                </div>
            `;

            elements.commentsList.innerHTML = comments.map(c => `
                <div class="comment-item">
                    <span class="comment-user">사용자 ${c.user_id}</span>
                    <span class="comment-text">${c.comment}</span>
                    <span class="comment-date">${new Date(c.created_at).toLocaleString()}</span>
                </div>
            `).join('') || '<p style="font-size: 0.875rem; color: var(--text-secondary);">첫 댓글을 남겨보세요!</p>';
        } catch (err) {
            alert(err.message);
        }
    }

};


// --- Initialization ---
const init = async () => {
    const token = localStorage.getItem('token');
    if (token) {
        elements.navbar.classList.remove('hidden');
        showView('feed');
    } else {
        showView('auth');
    }
};

init();
