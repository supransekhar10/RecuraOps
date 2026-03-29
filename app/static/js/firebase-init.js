// RecuraOps — Firebase Login Handler
const FIREBASE_CONFIG = window.FIREBASE_CONFIG || {};
firebase.initializeApp(FIREBASE_CONFIG);
const auth = firebase.auth();

const loginForm  = document.getElementById('login-form');
const emailInput = document.getElementById('email');
const passInput  = document.getElementById('password');
const errorBox   = document.getElementById('error-box');
const submitBtn  = document.getElementById('submit-btn');
const btnText    = document.getElementById('btn-text');
const btnSpinner = document.getElementById('btn-spinner');

function showError(msg) {
  errorBox.querySelector('span').textContent = msg;
  errorBox.style.display = 'flex';
  errorBox.classList.add('shake');
  setTimeout(() => errorBox.classList.remove('shake'), 500);
}
function setLoading(v) {
  submitBtn.disabled = v;
  btnText.textContent = v ? 'Signing in…' : 'Sign In';
  btnSpinner.style.display = v ? 'inline-block' : 'none';
}

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  errorBox.style.display = 'none';
  const email = emailInput.value.trim();
  const password = passInput.value;
  if (!email || !password) { showError('Please enter your email and password.'); return; }
  setLoading(true);
  try {
    const cred = await auth.signInWithEmailAndPassword(email, password);
    const idToken = await cred.user.getIdToken();
    const res = await fetch('/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({idToken}),
    });
    const data = await res.json();
    if (data.success) {
      window.location.href = data.redirect;
    } else {
      setLoading(false);
      showError(data.error || 'Login failed. Please try again.');
    }
  } catch (err) {
    setLoading(false);
    let msg = 'Invalid email or password.';
    if (err.code === 'auth/user-not-found') msg = 'No account found with this email.';
    if (err.code === 'auth/wrong-password') msg = 'Incorrect password.';
    if (err.code === 'auth/too-many-requests') msg = 'Too many attempts. Please wait.';
    showError(msg);
  }
});

document.getElementById('toggle-password').addEventListener('click', () => {
  const t = passInput.type === 'password' ? 'text' : 'password';
  passInput.type = t;
  document.getElementById('toggle-password').innerHTML =
    t === 'text'
      ? '<i data-lucide="eye-off" style="width:16px;height:16px"></i>'
      : '<i data-lucide="eye" style="width:16px;height:16px"></i>';
  lucide.createIcons();
});

document.querySelectorAll('.demo-cred').forEach(btn => {
  btn.addEventListener('click', () => {
    emailInput.value = btn.dataset.email;
    passInput.value  = btn.dataset.password;
    errorBox.style.display = 'none';
  });
});
