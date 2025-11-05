-- ============================================
-- retroNet Database Schema (SQLite)
-- An authentic retro social media experience
-- ============================================

-- ============================================
-- USER MANAGEMENT
-- ============================================

-- Main user table
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    profile_customized INTEGER DEFAULT 0,
    profile_mthl TEXT, -- MTHL code for profile customization
    profile_background_color TEXT DEFAULT '#000000',
    profile_text_color TEXT DEFAULT '#00FF00',
    invite_key TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    stalker_count INTEGER DEFAULT 0, -- denormalized for performance
    stalking_count INTEGER DEFAULT 0 -- who this user stalks
);

-- Stalker relationships (following/followers)
-- stalker_id is the person doing the stalking (follower)
-- stalked_id is the person being stalked (followee)
CREATE TABLE IF NOT EXISTS stalker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stalker_id INTEGER NOT NULL,
    stalked_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stalker_id) REFERENCES user (id) ON DELETE CASCADE,
    FOREIGN KEY (stalked_id) REFERENCES user (id) ON DELETE CASCADE,
    UNIQUE(stalker_id, stalked_id) -- prevent duplicate stalking
);

-- ============================================
-- MUSIC
-- ============================================

-- User's music playlist
CREATE TABLE IF NOT EXISTS user_music (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    spotify_track_id TEXT NOT NULL,
    track_name TEXT,
    artist_name TEXT,
    album_name TEXT,
    track_order INTEGER DEFAULT 0, -- for ordering songs
    is_profile_song INTEGER DEFAULT 0, -- 1 if this plays on profile
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE
);

-- ============================================
-- BLOG POSTS
-- ============================================

-- User blog posts
CREATE TABLE IF NOT EXISTS user_blog_post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    is_published INTEGER DEFAULT 1,
    view_count INTEGER DEFAULT 0,
    FOREIGN KEY (author_id) REFERENCES user (id) ON DELETE CASCADE
);

-- Blog post reactions (likes, etc.)
CREATE TABLE IF NOT EXISTS blog_post_reaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    reaction_type TEXT NOT NULL, -- 'like', 'cool', 'radical', 'tubular'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES user_blog_post (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    UNIQUE(post_id, user_id, reaction_type)
);

-- ============================================
-- FORUMS
-- ============================================

-- Forum categories
CREATE TABLE IF NOT EXISTS forum (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    post_count INTEGER DEFAULT 0,
    subscriber_count INTEGER DEFAULT 0,
    FOREIGN KEY (created_by) REFERENCES user (id)
);

-- Forum threads
CREATE TABLE IF NOT EXISTS forum_thread (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forum_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_pinned INTEGER DEFAULT 0,
    is_locked INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    FOREIGN KEY (forum_id) REFERENCES forum (id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES user (id)
);

-- Forum posts (replies to threads)
CREATE TABLE IF NOT EXISTS forum_post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_edited INTEGER DEFAULT 0,
    FOREIGN KEY (thread_id) REFERENCES forum_thread (id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES user (id)
);

-- Forum post reactions
CREATE TABLE IF NOT EXISTS forum_post_reaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    reaction_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES forum_post (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    UNIQUE(post_id, user_id, reaction_type)
);

-- Forum subscriptions
CREATE TABLE IF NOT EXISTS forum_subscription (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    forum_id INTEGER NOT NULL,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    FOREIGN KEY (forum_id) REFERENCES forum (id) ON DELETE CASCADE,
    UNIQUE(user_id, forum_id)
);

-- ============================================
-- USENET GROUPS
-- ============================================

-- Usenet-style newsgroups
CREATE TABLE IF NOT EXISTS usenet_group (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL, -- e.g., 'alt.retronet.general'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    post_count INTEGER DEFAULT 0,
    subscriber_count INTEGER DEFAULT 0
);

-- Usenet posts (articles)
CREATE TABLE IF NOT EXISTS usenet_post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    parent_id INTEGER, -- for threading (replies)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_id TEXT UNIQUE, -- RFC-style message ID
    FOREIGN KEY (group_id) REFERENCES usenet_group (id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES user (id),
    FOREIGN KEY (parent_id) REFERENCES usenet_post (id) ON DELETE CASCADE
);

-- Usenet group subscriptions
CREATE TABLE IF NOT EXISTS usenet_subscription (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES usenet_group (id) ON DELETE CASCADE,
    UNIQUE(user_id, group_id)
);

-- ============================================
-- FEED & ALGORITHM
-- ============================================

-- User feed preferences (for anti-influencer algorithm)
CREATE TABLE IF NOT EXISTS user_feed_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    show_stalker_posts INTEGER DEFAULT 1,
    show_forum_posts INTEGER DEFAULT 1,
    show_usenet_posts INTEGER DEFAULT 1,
    show_blog_posts INTEGER DEFAULT 1,
    sort_by TEXT DEFAULT 'chronological', -- 'chronological', 'random', 'anti-popular'
    filter_keywords TEXT, -- JSON array of keywords to filter
    boost_keywords TEXT, -- JSON array of keywords to boost
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    UNIQUE(user_id)
);

-- ============================================
-- VISITORS & ANALYTICS
-- ============================================

-- Track unique visitors to the site
CREATE TABLE IF NOT EXISTS visitors (
    visitor_id TEXT PRIMARY KEY,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track profile views
CREATE TABLE IF NOT EXISTS profile_view (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_user_id INTEGER NOT NULL,
    viewer_user_id INTEGER, -- NULL if anonymous
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_user_id) REFERENCES user (id) ON DELETE CASCADE,
    FOREIGN KEY (viewer_user_id) REFERENCES user (id) ON DELETE SET NULL
);

-- ============================================
-- INVITES
-- ============================================

-- Invite tracking for closed beta/community
CREATE TABLE IF NOT EXISTS invite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invite_code TEXT UNIQUE NOT NULL,
    created_by INTEGER NOT NULL,
    used_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (created_by) REFERENCES user (id),
    FOREIGN KEY (used_by) REFERENCES user (id)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- User indexes
CREATE INDEX IF NOT EXISTS idx_user_last_seen ON user(last_seen);
CREATE INDEX IF NOT EXISTS idx_user_profile_customized ON user(profile_customized);
CREATE INDEX IF NOT EXISTS idx_user_username ON user(username);

-- Stalker indexes
CREATE INDEX IF NOT EXISTS idx_stalker_stalker_id ON stalker(stalker_id);
CREATE INDEX IF NOT EXISTS idx_stalker_stalked_id ON stalker(stalked_id);
CREATE INDEX IF NOT EXISTS idx_stalker_created_at ON stalker(created_at);

-- Music indexes
CREATE INDEX IF NOT EXISTS idx_user_music_user_id ON user_music(user_id);
CREATE INDEX IF NOT EXISTS idx_user_music_profile_song ON user_music(user_id, is_profile_song);

-- Blog indexes
CREATE INDEX IF NOT EXISTS idx_user_blog_post_author ON user_blog_post(author_id);
CREATE INDEX IF NOT EXISTS idx_user_blog_post_created ON user_blog_post(created_at);
CREATE INDEX IF NOT EXISTS idx_blog_reaction_post ON blog_post_reaction(post_id);

-- Forum indexes
CREATE INDEX IF NOT EXISTS idx_forum_thread_forum ON forum_thread(forum_id);
CREATE INDEX IF NOT EXISTS idx_forum_thread_author ON forum_thread(author_id);
CREATE INDEX IF NOT EXISTS idx_forum_thread_activity ON forum_thread(last_activity);
CREATE INDEX IF NOT EXISTS idx_forum_post_thread ON forum_post(thread_id);
CREATE INDEX IF NOT EXISTS idx_forum_post_author ON forum_post(author_id);
CREATE INDEX IF NOT EXISTS idx_forum_subscription_user ON forum_subscription(user_id);
CREATE INDEX IF NOT EXISTS idx_forum_subscription_forum ON forum_subscription(forum_id);

-- Usenet indexes
CREATE INDEX IF NOT EXISTS idx_usenet_post_group ON usenet_post(group_id);
CREATE INDEX IF NOT EXISTS idx_usenet_post_author ON usenet_post(author_id);
CREATE INDEX IF NOT EXISTS idx_usenet_post_parent ON usenet_post(parent_id);
CREATE INDEX IF NOT EXISTS idx_usenet_subscription_user ON usenet_subscription(user_id);
CREATE INDEX IF NOT EXISTS idx_usenet_subscription_group ON usenet_subscription(group_id);

-- Visitor indexes
CREATE INDEX IF NOT EXISTS idx_visitors_last_seen ON visitors(last_seen);
CREATE INDEX IF NOT EXISTS idx_profile_view_profile ON profile_view(profile_user_id);
CREATE INDEX IF NOT EXISTS idx_profile_view_viewer ON profile_view(viewer_user_id);

-- Invite indexes
CREATE INDEX IF NOT EXISTS idx_invite_code ON invite(invite_code);
CREATE INDEX IF NOT EXISTS idx_invite_created_by ON invite(created_by);
CREATE INDEX IF NOT EXISTS idx_invite_used_by ON invite(used_by);

-- ============================================
-- TRIGGERS FOR DENORMALIZATION
-- ============================================

-- Update stalker counts when stalker relationships change
CREATE TRIGGER IF NOT EXISTS update_stalker_count_on_insert
AFTER INSERT ON stalker
BEGIN
    UPDATE user SET stalker_count = stalker_count + 1 WHERE id = NEW.stalked_id;
    UPDATE user SET stalking_count = stalking_count + 1 WHERE id = NEW.stalker_id;
END;

CREATE TRIGGER IF NOT EXISTS update_stalker_count_on_delete
AFTER DELETE ON stalker
BEGIN
    UPDATE user SET stalker_count = stalker_count - 1 WHERE id = OLD.stalked_id;
    UPDATE user SET stalking_count = stalking_count - 1 WHERE id = OLD.stalker_id;
END;

-- Update forum post counts
CREATE TRIGGER IF NOT EXISTS update_forum_post_count_on_insert
AFTER INSERT ON forum_thread
BEGIN
    UPDATE forum SET post_count = post_count + 1 WHERE id = NEW.forum_id;
END;

CREATE TRIGGER IF NOT EXISTS update_forum_post_count_on_delete
AFTER DELETE ON forum_thread
BEGIN
    UPDATE forum SET post_count = post_count - 1 WHERE id = OLD.forum_id;
END;

-- Update thread reply counts
CREATE TRIGGER IF NOT EXISTS update_thread_reply_count_on_insert
AFTER INSERT ON forum_post
BEGIN
    UPDATE forum_thread SET reply_count = reply_count + 1, last_activity = CURRENT_TIMESTAMP WHERE id = NEW.thread_id;
END;

CREATE TRIGGER IF NOT EXISTS update_thread_reply_count_on_delete
AFTER DELETE ON forum_post
BEGIN
    UPDATE forum_thread SET reply_count = reply_count - 1 WHERE id = OLD.thread_id;
END;

-- Update usenet post counts
CREATE TRIGGER IF NOT EXISTS update_usenet_post_count_on_insert
AFTER INSERT ON usenet_post
BEGIN
    UPDATE usenet_group SET post_count = post_count + 1 WHERE id = NEW.group_id;
END;

CREATE TRIGGER IF NOT EXISTS update_usenet_post_count_on_delete
AFTER DELETE ON usenet_post
BEGIN
    UPDATE usenet_group SET post_count = post_count - 1 WHERE id = OLD.group_id;
END;

-- Update subscription counts
CREATE TRIGGER IF NOT EXISTS update_forum_sub_count_on_insert
AFTER INSERT ON forum_subscription
BEGIN
    UPDATE forum SET subscriber_count = subscriber_count + 1 WHERE id = NEW.forum_id;
END;

CREATE TRIGGER IF NOT EXISTS update_forum_sub_count_on_delete
AFTER DELETE ON forum_subscription
BEGIN
    UPDATE forum SET subscriber_count = subscriber_count - 1 WHERE id = OLD.forum_id;
END;

CREATE TRIGGER IF NOT EXISTS update_usenet_sub_count_on_insert
AFTER INSERT ON usenet_subscription
BEGIN
    UPDATE usenet_group SET subscriber_count = subscriber_count + 1 WHERE id = NEW.group_id;
END;

CREATE TRIGGER IF NOT EXISTS update_usenet_sub_count_on_delete
AFTER DELETE ON usenet_subscription
BEGIN
    UPDATE usenet_group SET subscriber_count = subscriber_count - 1 WHERE id = OLD.group_id;
END;
