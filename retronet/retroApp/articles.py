from flask import redirect, url_for, request, render_template
from markupsafe import escape, Markup
from .dummy import NEWSGROUPS, ARTICLES

def article_tools(app):

    @app.template_filter('format_message')
    def format_message(text):
        """Format message body with proper styling for quotes and signatures"""
        if not text:
            return ''
        
        lines = text.split('\n')
        formatted_lines = []
        in_signature = False
        
        for line in lines:
            # Check for signature delimiter
            if line.strip() == '--':
                in_signature = True
                formatted_lines.append('<div class="signature">')
                formatted_lines.append(escape(line))
                continue
            
            if in_signature:
                formatted_lines.append(escape(line))
                continue
            
            # Count quote depth
            quote_depth = 0
            stripped = line
            while stripped.startswith('>'):
                quote_depth += 1
                stripped = stripped[1:].lstrip()
            
            if quote_depth > 0:
                css_class = f'quoted-line quoted-line-{min(quote_depth, 3)}'
                formatted_lines.append(f'<span class="{css_class}">{escape(line)}</span>')
            else:
                formatted_lines.append(escape(line))
        
        if in_signature:
            formatted_lines.append('</div>')
        
        return Markup('\n'.join(formatted_lines))

    @app.route('/article/<int:article_id>')
    def view_article(article_id):
        """View a specific article"""
        article = next((a for a in ARTICLES if a['id'] == article_id), None)
        if not article:
            return redirect(url_for('usenet.usenet'))
        
        group = next((g for g in NEWSGROUPS if g['id'] == article['newsgroup_id']), None)
        
        # Get all articles for the thread view
        articles = [a for a in ARTICLES if a['newsgroup_id'] == article['newsgroup_id']]
        threads = build_threads(articles)
        
        categories = build_categories()
        
        return render_template('usenet/index.html',
                            categories=categories,
                            selected_group=group,
                            threads=threads,
                            selected_article=article)
    

    @app.route('/post/<int:group_id>', methods=['GET', 'POST'])
    def post_article(group_id):
        """Post a new article"""
        group = next((g for g in NEWSGROUPS if g['id'] == group_id), None)
        if not group:
            return redirect(url_for('usenet.usenet'))
        
        if request.method == 'POST':
            # Handle post submission
            # This would save to database in real implementation
            return redirect(url_for('view_group', group_id=group_id))
        
        return render_template('usenet/post.html', group=group, reply_to=None)

    @app.route('/reply/<int:article_id>', methods=['GET', 'POST'])
    def reply_article(article_id):
        """Reply to an article"""
        article = next((a for a in ARTICLES if a['id'] == article_id), None)
        if not article:
            return redirect(url_for('usenet.usenet'))
        
        group = next((g for g in NEWSGROUPS if g['id'] == article['newsgroup_id']), None)
        
        if request.method == 'POST':
            # Handle reply submission
            return redirect(url_for('view_group', group_id=group['id']))
        
        return render_template('usenet/post.html', group=group, reply_to=article)
    
    @app.route('/group/<int:group_id>')
    def view_group(group_id):
        """View a specific newsgroup"""
        group = next((g for g in NEWSGROUPS if g['id'] == group_id), None)
        if not group:
            return redirect(url_for('usenet.usenet'))
        
        # Get articles for this group
        articles = [a for a in ARTICLES if a['newsgroup_id'] == group_id]
        
        # Build thread structure
        threads = build_threads(articles)
        
        categories = build_categories()
        
        return render_template('usenet/index.html',
                            categories=categories,
                            selected_group=group,
                            threads=threads,
                            selected_article=None)

def build_categories():
    """Group the newsgroup list by category for the newsreader's left pane."""
    categories = {}
    for group in NEWSGROUPS:
        categories.setdefault(group['category'], []).append(group)
    return categories


def build_threads(articles):
    """Build threaded structure from flat article list"""
    # Create lookup dict
    article_dict = {a['id']: a.copy() for a in articles}
    
    # Add children list to each article
    for article in article_dict.values():
        article['children'] = []
    
    # Build tree
    roots = []
    for article in article_dict.values():
        if article['parent_id'] is None:
            roots.append(article)
        else:
            parent = article_dict.get(article['parent_id'])
            if parent:
                parent['children'].append(article)
    
    return roots