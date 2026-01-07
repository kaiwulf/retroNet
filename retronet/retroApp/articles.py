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
            return redirect(url_for('index'))
        
        group = next((g for g in NEWSGROUPS if g['id'] == article['newsgroup_id']), None)
        
        # Get all articles for the thread view
        articles = [a for a in ARTICLES if a['newsgroup_id'] == article['newsgroup_id']]
        threads = build_threads(articles)
        
        # Group newsgroups by category
        categories = {}
        for g in NEWSGROUPS:
            cat = g['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(g)
        
        return render_template('index.html',
                            categories=categories,
                            selected_group=group,
                            threads=threads,
                            selected_article=article)
    

    @app.route('/post/<int:group_id>', methods=['GET', 'POST'])
    def post_article(group_id):
        """Post a new article"""
        group = next((g for g in NEWSGROUPS if g['id'] == group_id), None)
        if not group:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            # Handle post submission
            # This would save to database in real implementation
            return redirect(url_for('view_group', group_id=group_id))
        
        return render_template('post.html', group=group, reply_to=None)

    @app.route('/reply/<int:article_id>', methods=['GET', 'POST'])
    def reply_article(article_id):
        """Reply to an article"""
        article = next((a for a in ARTICLES if a['id'] == article_id), None)
        if not article:
            return redirect(url_for('index'))
        
        group = next((g for g in NEWSGROUPS if g['id'] == article['newsgroup_id']), None)
        
        if request.method == 'POST':
            # Handle reply submission
            return redirect(url_for('view_group', group_id=group['id']))
        
        return render_template('post.html', group=group, reply_to=article)