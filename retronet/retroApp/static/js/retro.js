// ═══════════════════════════════════════════════════════════
// retroNet JavaScript - Making the Web Fun Again!
// ═══════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', function() {
    console.log('%c🌐 Welcome to retroNet! 🌐', 'font-size: 20px; color: #ff00ff; text-shadow: 2px 2px #00ffff;');
    console.log('%cRemember: If your eyes don\'t hurt, we\'re not doing it right! 😎', 'font-size: 14px; color: #00ffff;');
    
    initVisitorCounter();
    initSparkles();
    initCursorTrail();
    initRandomGlitter();
    playRetroSounds();
});

// === VISITOR COUNTER (Classic 90s) ===
function initVisitorCounter() {
    const counter = document.getElementById('visitor-count');
    if (!counter) return;
    
    // Load from localStorage or start at 1337
    let count = parseInt(localStorage.getItem('retronet-visitors') || '1337');
    
    // Increment on each visit
    count += Math.floor(Math.random() * 5) + 1;
    localStorage.setItem('retronet-visitors', count.toString());
    
    // Animate the counter
    animateCounter(counter, count);
    
    // Randomly increment (like the old days where counters were totally fake)
    setInterval(() => {
        count += Math.floor(Math.random() * 3);
        localStorage.setItem('retronet-visitors', count.toString());
        counter.textContent = String(count).padStart(6, '0');
    }, 10000);
}

function animateCounter(element, targetCount) {
    let currentCount = targetCount - 50;
    const interval = setInterval(() => {
        currentCount += Math.floor(Math.random() * 5) + 1;
        if (currentCount >= targetCount) {
            currentCount = targetCount;
            clearInterval(interval);
        }
        element.textContent = String(currentCount).padStart(6, '0');
    }, 50);
}

// === FLOATING SPARKLES ===
function initSparkles() {
    const sparkles = ['✨', '⭐', '🌟', '💫', '⚡', '💖', '🌈'];
    
    setInterval(() => {
        createSparkle(sparkles[Math.floor(Math.random() * sparkles.length)]);
    }, 2000);
}

function createSparkle(emoji) {
    const sparkle = document.createElement('div');
    sparkle.className = 'floating-sparkle';
    sparkle.textContent = emoji;
    sparkle.style.left = Math.random() * 100 + '%';
    sparkle.style.animationDuration = (Math.random() * 3 + 2) + 's';
    sparkle.style.fontSize = (Math.random() * 1.5 + 1) + 'em';
    
    document.body.appendChild(sparkle);
    
    setTimeout(() => {
        sparkle.remove();
    }, 5000);
}

// === CURSOR TRAIL (Very MySpace) ===
function initCursorTrail() {
    const colors = ['#ff00ff', '#00ffff', '#ffff00', '#00ff00', '#ff0000'];
    let lastX = 0;
    let lastY = 0;
    let trailTimer = null;
    
    document.addEventListener('mousemove', function(e) {
        // Throttle to avoid performance issues
        if (Math.abs(e.clientX - lastX) < 10 && Math.abs(e.clientY - lastY) < 10) return;
        
        lastX = e.clientX;
        lastY = e.clientY;
        
        if (trailTimer) clearTimeout(trailTimer);
        
        trailTimer = setTimeout(() => {
            createTrailDot(e.clientX, e.clientY, colors[Math.floor(Math.random() * colors.length)]);
        }, 50);
    });
}

function createTrailDot(x, y, color) {
    const dot = document.createElement('div');
    dot.style.position = 'fixed';
    dot.style.left = x + 'px';
    dot.style.top = y + 'px';
    dot.style.width = '8px';
    dot.style.height = '8px';
    dot.style.borderRadius = '50%';
    dot.style.backgroundColor = color;
    dot.style.pointerEvents = 'none';
    dot.style.zIndex = '9998';
    dot.style.boxShadow = `0 0 10px ${color}`;
    dot.style.transition = 'opacity 0.5s';
    
    document.body.appendChild(dot);
    
    setTimeout(() => {
        dot.style.opacity = '0';
    }, 100);
    
    setTimeout(() => {
        dot.remove();
    }, 600);
}

// === RANDOM GLITTER TEXT EFFECTS ===
function initRandomGlitter() {
    const glitterElements = document.querySelectorAll('.glitter-text, .rainbow-text');
    
    glitterElements.forEach(element => {
        setInterval(() => {
            element.style.filter = `hue-rotate(${Math.random() * 360}deg)`;
        }, 2000);
    });
}

// === RETRO SOUND EFFECTS (Optional - very annoying!) ===
function playRetroSounds() {
    // Only play sounds if user interacts (browsers block auto-play)
    let soundsEnabled = false;
    
    document.addEventListener('click', function enableSounds() {
        if (!soundsEnabled) {
            soundsEnabled = true;
            console.log('🔊 Retro sounds activated! (Just kidding, we respect your ears)');
        }
    }, { once: true });
}

// === KONAMI CODE (Easter Egg!) ===
(function() {
    const konamiCode = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // ↑↑↓↓←→←→BA
    let konamiIndex = 0;
    
    document.addEventListener('keydown', function(e) {
        if (e.keyCode === konamiCode[konamiIndex]) {
            konamiIndex++;
            
            if (konamiIndex === konamiCode.length) {
                activateKonamiCode();
                konamiIndex = 0;
            }
        } else {
            konamiIndex = 0;
        }
    });
    
    function activateKonamiCode() {
        alert('🎮 KONAMI CODE ACTIVATED! 🎮\n\nYou found the secret! You get... EXTRA SPARKLES! ✨✨✨');
        
        // Sparkle overload!
        for (let i = 0; i < 50; i++) {
            setTimeout(() => {
                createSparkle(['✨', '⭐', '🌟'][Math.floor(Math.random() * 3)]);
            }, i * 100);
        }
        
        // Change background temporarily
        document.body.style.animation = 'rainbowBackground 5s ease infinite';
    }
})();

// === PROFILE MUSIC PLAYER (Placeholder) ===
function initMusicPlayer() {
    console.log('🎵 Music player initialized (coming soon!)');
    console.log('💡 Tip: Auto-playing music will be BACK, baby!');
}

// === MTHL PARSER (Placeholder for future implementation) ===
function parseMTHL(content) {
    console.log('📝 MTHL parsing coming soon!');
    return content;
}

// === RANDOM PAGE TITLE CHANGES (Very Annoying!) ===
(function() {
    const titles = [
        '✨ retroNet ✨',
        '🌟 retroNet - Come Back! 🌟',
        '💖 retroNet - Miss You! 💖',
        '🎵 retroNet - Check This Out! 🎵',
        '👀 retroNet - Someone\'s Stalking You! 👀'
    ];
    
    let titleIndex = 0;
    let originalTitle = document.title;
    
    // Only change title when page is not focused
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            setInterval(() => {
                document.title = titles[titleIndex % titles.length];
                titleIndex++;
            }, 2000);
        } else {
            document.title = originalTitle;
        }
    });
})();

// === POLL VOTING ===
document.addEventListener('click', function(e) {
    if (e.target.matches('.survey-box button')) {
        const selected = document.querySelector('.survey-box input[type="radio"]:checked');
        if (selected) {
            alert('Thanks for voting! Your vote totally matters! (It doesn\'t, but we appreciate it anyway 😊)');
        } else {
            alert('Please select an option first! 📊');
        }
    }
});

// === LINK ANIMATIONS ===
document.querySelectorAll('a').forEach(link => {
    link.addEventListener('mouseenter', function() {
        if (Math.random() > 0.7) { // 30% chance
            createSparkle('✨');
        }
    });
});

// === PREVENT RIGHT-CLICK (Classic 90s Annoyance - Optional) ===
// Uncomment if you want to be truly authentic (and annoying)
/*
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    alert('Right-clicking is disabled! This is MY page! 😤');
    return false;
});
*/

// === STATUS BAR MESSAGES (If we had a status bar) ===
window.addEventListener('load', function() {
    console.log('✅ Page loaded successfully!');
    console.log('👾 Ready to rock the retro web!');
});

// === RANDOM FACTS (Console Easter Eggs) ===
const retroFacts = [
    'Did you know? MySpace was launched in 2003!',
    'Fun fact: GeoCities had over 38 million pages at its peak!',
    'Remember when you needed to ask "A/S/L?" in chat rooms?',
    'Tom from MySpace was everyone\'s first friend!',
    'The <blink> tag was deprecated in 2013 (RIP 🪦)',
    'Comic Sans was designed in 1994 and has been controversial ever since!',
    'The dancing baby GIF is from 1996 and haunts us still!'
];

console.log(`\n💡 Random Retro Fact: ${retroFacts[Math.floor(Math.random() * retroFacts.length)]}\n`);

// === EXPORT FOR USE IN OTHER SCRIPTS ===
window.retroNet = {
    createSparkle: createSparkle,
    parseMTHL: parseMTHL,
    initMusicPlayer: initMusicPlayer
};

// ═══════════════════════════════════════════════════════════
// Live Stats with AJAX Polling
// ═══════════════════════════════════════════════════════════

let statsUpdateInterval = null;
let failedAttempts = 0;
const MAX_FAILED_ATTEMPTS = 5;

function startStatsPolling() {
    console.log('🚀 Starting live stats polling...');
    
    // Initial update
    updateStats();
    
    // Poll every 5 seconds
    statsUpdateInterval = setInterval(updateStats, 5000);
}

function stopStatsPolling() {
    if (statsUpdateInterval) {
        clearInterval(statsUpdateInterval);
        statsUpdateInterval = null;
        console.log('🛑 Stats polling stopped');
    }
}

function updateStats() {
    fetch('/api/stats')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(stats => {
            // Reset failed attempts on success
            failedAttempts = 0;
            
            console.log('📊 Stats updated:', stats);
            
            // Update visitor counter
            updateVisitorCounter(stats.visitors);
            
            // Update stats
            updateStat('total-members', stats.members);
            updateStat('active-now', stats.active_now);
            updateStat('profiles-pimped', stats.profiles_pimped);
            updateStat('songs-playing', stats.songs_playing);
        })
        .catch(err => {
            failedAttempts++;
            console.error(`❌ Stats update failed (${failedAttempts}/${MAX_FAILED_ATTEMPTS}):`, err);
            
            // Stop polling after too many failures
            if (failedAttempts >= MAX_FAILED_ATTEMPTS) {
                console.error('❌ Too many failed attempts, stopping polling');
                stopStatsPolling();
                
                // Try to restart after a longer delay
                setTimeout(() => {
                    console.log('🔄 Attempting to restart stats polling...');
                    failedAttempts = 0;
                    startStatsPolling();
                }, 30000); // 30 seconds
            }
        });
}

// Update visitor counter with smooth animation
function updateVisitorCounter(count) {
    const counter = document.getElementById('visitor-count');
    if (!counter) return;
    
    const currentCount = parseInt(counter.textContent.replace(/\D/g, '')) || 0;
    const targetCount = count;
    
    // If difference is small, animate the counting
    if (Math.abs(targetCount - currentCount) < 100 && targetCount !== currentCount) {
        animateCounter(counter, currentCount, targetCount, 1000);
    } else if (targetCount !== currentCount) {
        // Large difference or initial load, just update directly
        counter.textContent = String(targetCount).padStart(6, '0');
        counter.classList.add('stat-pulse');
        setTimeout(() => counter.classList.remove('stat-pulse'), 500);
    }
}

// Animate counter from start to end value
function animateCounter(element, start, end, duration) {
    const startTime = Date.now();
    const difference = end - start;
    
    function update() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Ease out animation
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + difference * easeOut);
        
        element.textContent = String(current).padStart(6, '0');
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            // Add pulse effect at the end
            element.classList.add('stat-pulse');
            setTimeout(() => element.classList.remove('stat-pulse'), 500);
        }
    }
    
    requestAnimationFrame(update);
}

// Update individual stat with animation
function updateStat(id, value) {
    const elem = document.getElementById(id);
    if (!elem) return;
    
    const currentValue = elem.textContent.trim();
    const newValue = String(value);
    
    // Only animate if value changed
    if (currentValue !== newValue) {
        // Add update animation
        elem.classList.add('stat-update');
        elem.textContent = newValue;
        
        // Remove animation class after it completes
        setTimeout(() => {
            elem.classList.remove('stat-update');
        }, 500);
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Only start polling on pages that have stats
    if (document.getElementById('visitor-count')) {
        console.log('🚀 Initializing live stats...');
        startStatsPolling();
    }
});

// Stop polling when page unloads
window.addEventListener('beforeunload', function() {
    stopStatsPolling();
});

// Pause when page is hidden, resume when visible
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        console.log('👁️ Page hidden, pausing stats polling');
        stopStatsPolling();
    } else {
        console.log('👁️ Page visible, resuming stats polling');
        if (document.getElementById('visitor-count')) {
            startStatsPolling();
        }
    }
});

// Expose control functions for debugging
window.startStats = startStatsPolling;
window.stopStats = stopStatsPolling;
window.updateStatsNow = updateStats;