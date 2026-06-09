#!/usr/bin/env python3
"""
pc_games_wine Games Grid Generator - OPTIMIZED for 16K+ games
Uses virtual scrolling to only render visible items
"""

import json
import os
import re
# Configuration
JSON_FILE = "pc_games_winejs.json"
OUTPUT_HTML = "pc_games_winejs.html"
PLACEHOLDER_IMAGE = "https://cdn.gitgpt.chat/rtx/images/pc-no-cover.png"
ITEMS_PER_PAGE = 100  # Load 100 games at a time

def load_games_data():
    """Load games from JSON file and remove duplicates by TITLE"""
    if not os.path.exists(JSON_FILE):
        print(f"❌ Error: {JSON_FILE} not found!")
        print("Please run the cover downloader first to generate the JSON file.")
        return None
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        games = json.load(f)
    
    # Remove duplicates by TITLE (keep first occurrence)
    seen_titles = set()
    unique_games = []
    for game in games:
        title = game['title'].lower().strip()
        if title not in seen_titles:
            seen_titles.add(title)
            unique_games.append(game)
    
    if len(unique_games) < len(games):
        print(f"✅ Removed {len(games) - len(unique_games)} duplicates by title")
    
    print(f"✅ Loaded {len(unique_games)} unique games from {JSON_FILE}")
    return unique_games

def generate_html(games):
    """Generate the grid website HTML with virtual scrolling"""
    
    games.sort(key=lambda x: x['title'].lower())
    
    total_games = len(games)
    with_covers = sum(1 for g in games if g.get('cover_url') and g['cover_url'] != PLACEHOLDER_IMAGE)
    
    # Pre-calculate search URLs for each game
    for game in games:
        # Create URL-friendly slug from title
        slug = game['title'].lower()
        # Remove special characters (keep letters, numbers, spaces, and hyphens)
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        # Replace multiple hyphens with single hyphen
        slug = re.sub(r'-+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        game['search_url'] = f"https://meyt.netlify.app/search/{slug}%20pc"

    # Convert games data to JSON for JavaScript
    games_json = json.dumps(games, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PC Games Collection - {total_games} Games</title>

  <link rel="icon" href="https://cdn.gitgpt.chat/rtx/images/gcw_logo_icon.png" type="image/png">
  <link rel="apple-touch-icon" href="https://cdn.gitgpt.chat/rtx/images/gcw_logo_icon.png" sizes="180x180">

  <style>
    body {{
      background-color: #1a1a1a;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      margin: 4px 20px;
      padding: 0;
    }}

    #results {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 10px;
      max-width: 1400px;
      margin: 0 auto;
      background-color: #1a1a1a;
      margin-top: 4px;
      z-index: 1000;
    }}

    .title-card {{
      background: #2a2a2a;
      border-radius: 8px;
      overflow: hidden;
      transition: transform 0.2s;
      opacity: 0;
      animation: fadeIn 0.3s ease forwards;
    }}

    @keyframes fadeIn {{
      from {{
        opacity: 0;
        transform: translateY(10px);
      }}
      to {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}

    .title-card:hover {{
      transform: scale(1.05);
      z-index: 10;
    }}

    .title-card-link {{
      display: block;
      text-decoration: none;
      color: inherit;
    }}

    .title-card-container {{
      width: 100%;
      position: relative;
    }}

    .title-card-image-container {{
      width: 100%;
      aspect-ratio: 3/5;
      overflow: hidden;
      position: relative;
      background-color: #1a1a1a;
    }}

    .title-card-image-container img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: opacity 0.3s;
    }}

    .title-card-image-container .fallback-title {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 10px;
      box-sizing: border-box;
      background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
      color: #888;
      font-size: 14px;
      font-weight: 500;
      word-break: break-word;
      border: 1px solid #333;
    }}

    .fill-color-Playable {{
      background-color: #42991b !important;
      color: white !important;
      font-weight: 700 !important;
    }}

    .card-body {{
      flex: 1 1 auto;
      min-height: 1px;
      padding: 0.5rem 1.25rem !important;
    }}

    .text-center {{
      text-align: center !important;
    }}

    .py-1 {{
      padding-top: 0.25rem !important;
      padding-bottom: 0.25rem !important;
    }}

    .my-0 {{
      margin-top: 0 !important;
      margin-bottom: 0 !important;
    }}

    small {{
      font-size: 80%;
    }}

    /* Search container */
    #saved-search-container {{
      position: sticky;
      top: 0;
      z-index: 10000;
      background-color: #1a1a1a;
      padding: 10px 0;
      margin-bottom: 10px;
    }}

    #saved-search-input {{
      padding: 10px;
      width: calc(100% - 20px);
      border: 1px solid #555;
      border-radius: 4px;
      background: #444;
      color: white;
      flex: 1;
    }}

    .search-row {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .icon {{
      width: 34px;
      height: 34px;
      border-radius: 4px;
      object-fit: cover;
    }}

    #saved-search-input::placeholder {{
      color: #aaa;
    }}

    #saved-results-count {{
      color: white;
      font-size: 14px;
      text-align: center;
      margin-top: 5px;
      margin-bottom: 0px;
      padding-bottom: 0px;
    }}

    /* Loading indicator */
    .loading-indicator {{
      text-align: center;
      padding: 40px;
      color: #888;
      grid-column: 1 / -1;
    }}

    .loading-spinner {{
      display: inline-block;
      width: 40px;
      height: 40px;
      border: 3px solid #333;
      border-top-color: #42991b;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }}

    @keyframes spin {{
      to {{ transform: rotate(360deg); }}
    }}

    /* Hide classes */
    .hidden-game {{
      display: none !important;
    }}

    /* Scroll to top button */
    #scroll-top {{
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: #42991b;
      color: white;
      border: none;
      border-radius: 50%;
      width: 50px;
      height: 50px;
      font-size: 24px;
      cursor: pointer;
      display: none;
      z-index: 10001;
      transition: all 0.3s;
    }}

    #scroll-top:hover {{
      transform: scale(1.1);
      background: #357a15;
    }}
  </style>
</head>

<body>
  <div id="saved-search-container">
    <div class="search-row">
      <img src="https://cdn.gitgpt.chat/rtx/images/gcw_logo_icon.png" class="icon" alt="GCW logo">
      <input type="text" id="saved-search-input" placeholder="Search {total_games} games... (Press '/' to focus)">
      <a href="https://igiteam.github.io/winejs/" target="_blank">
        <img src="https://cdn.gitgpt.chat/rtx/images/pcmouse.png" class="icon" alt="PC">
      </a>
      <a href="https://cdn.gitgpt.chat/rtx/pczone_magazine.html" target="_blank">
        <img src="https://cdn.gitgpt.chat/rtx/images/PCZONE%20-%20065%20(July%20'98)_Page_001.jpg" class="icon" alt="PC Magazine">
      </a>
    </div>
    <div id="saved-results-count">📊 Loading games... ({total_games} total)</div>
  </div>

  <div id="results"></div>
  <button id="scroll-top" title="Back to top">↑</button>

  <script>
    // Game data
    const allGames = {games_json};
    const PLACEHOLDER_IMAGE = "{PLACEHOLDER_IMAGE}";
    const ITEMS_PER_PAGE = {ITEMS_PER_PAGE};
    
    let currentIndex = 0;
    let isLoading = false;
    let searchTerm = '';
    let filteredGames = [...allGames];
    
    const resultsContainer = document.getElementById('results');
    const searchInput = document.getElementById('saved-search-input');
    const resultsCount = document.getElementById('saved-results-count');
    const scrollTopBtn = document.getElementById('scroll-top');
    
    // Create a game card element with its unique search URL
    function createGameCard(game, index) {{
      const title = game.title.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
      const hasRealCover = game.cover_url && game.cover_url !== PLACEHOLDER_IMAGE;
      const coverUrl = hasRealCover ? game.cover_url : PLACEHOLDER_IMAGE;
      const titleDisplay = hasRealCover ? 'none' : 'flex';
      const searchUrl = game.search_url;
      
      const card = document.createElement('div');
      card.className = 'title-card';
      card.setAttribute('data-title-name', title);
      card.setAttribute('data-title-status', 'Play');
      card.setAttribute('data-original-index', index);
      
      card.innerHTML = `
        <a target="_blank" rel="noopener noreferrer" href="${{searchUrl}}">
          <div class="title-card-container">
            <div class="title-card-image-container" style="position: relative;">
              <img
                src="${{coverUrl}}"
                loading="lazy"
                title="${{title}}"
                onerror="handleImageError(this)">
              <div class="fallback-title" style="display: ${{titleDisplay}};">${{title}}</div>
            </div>
            <div class="fill-color-Playable card-body text-center py-1 my-0">
              <small><strong>Play</strong></small>
            </div>
          </div>
        </a>
      `;
      
      return card;
    }}
    
    // Handle image loading errors
    window.handleImageError = function(img) {{
      const card = img.closest('.title-card');
      if (card) {{
        const fallbackDiv = card.querySelector('.fallback-title');
        if (fallbackDiv) {{
          fallbackDiv.style.display = 'flex';
        }}
        img.style.display = 'none';
      }}
    }};
    
    // Load more games
    function loadMoreGames() {{
      if (isLoading) return;
      if (currentIndex >= filteredGames.length) return;
      
      isLoading = true;
      
      // Show loading indicator
      const loadingDiv = document.createElement('div');
      loadingDiv.className = 'loading-indicator';
      loadingDiv.id = 'loading-indicator';
      loadingDiv.innerHTML = '<div class="loading-spinner"></div><div>Loading more games...</div>';
      resultsContainer.appendChild(loadingDiv);
      
      // Use setTimeout to avoid blocking UI
      setTimeout(() => {{
        const endIndex = Math.min(currentIndex + ITEMS_PER_PAGE, filteredGames.length);
        const fragment = document.createDocumentFragment();
        
        for (let i = currentIndex; i < endIndex; i++) {{
          const card = createGameCard(filteredGames[i], i);
          fragment.appendChild(card);
        }}
        
        // Remove loading indicator
        const loadingElem = document.getElementById('loading-indicator');
        if (loadingElem) loadingElem.remove();
        
        resultsContainer.appendChild(fragment);
        currentIndex = endIndex;
        isLoading = false;
        
        // Update results count
        updateResultsCount();
      }}, 50);
    }}
    
    // Update results count display
    function updateResultsCount() {{
      if (searchTerm) {{
        resultsCount.textContent = `🔍 Found ${{filteredGames.length}} game${{filteredGames.length !== 1 ? 's' : ''}} for "${{searchTerm}}" (Showing ${{currentIndex}} of ${{filteredGames.length}})`;
      }} else {{
        resultsCount.textContent = ``;
      }}
    }}
    
    // Filter games based on search term
    function filterGames() {{
      const term = searchInput.value.toLowerCase().trim();
      searchTerm = term;
      
      if (!term) {{
        filteredGames = [...allGames];
      }} else {{
        filteredGames = allGames.filter(game => 
          game.title.toLowerCase().includes(term)
        );
      }}
      
      // Reset and reload
      currentIndex = 0;
      resultsContainer.innerHTML = '';
      loadMoreGames();
    }}
    
    // Infinite scroll detection
    function handleScroll() {{
      // Show/hide scroll to top button
      if (window.pageYOffset > 300) {{
        scrollTopBtn.style.display = 'block';
      }} else {{
        scrollTopBtn.style.display = 'none';
      }}
      
      // Load more when near bottom
      const scrollPosition = window.innerHeight + window.scrollY;
      const threshold = document.body.offsetHeight - 500;
      
      if (scrollPosition >= threshold && !isLoading && currentIndex < filteredGames.length) {{
        loadMoreGames();
      }}
    }}
    
    // Scroll to top
    function scrollToTop() {{
      window.scrollTo({{
        top: 0,
        behavior: 'smooth'
      }});
    }}
    
    // Event listeners
    searchInput.addEventListener('input', () => {{
      filterGames();
    }});
    
    window.addEventListener('scroll', handleScroll);
    scrollTopBtn.addEventListener('click', scrollToTop);
    
    // Keyboard shortcut
    document.addEventListener('keydown', function(e) {{
      if (e.key === '/' && document.activeElement !== searchInput) {{
        e.preventDefault();
        searchInput.focus();
      }}
      if (e.key === 'Escape' && document.activeElement === searchInput) {{
        searchInput.value = '';
        filterGames();
        searchInput.blur();
      }}
    }});
    
    // Initial load
    loadMoreGames();
    
    // Add stats in console
    console.log(`🎮 Loaded {total_games} games, ${{with_covers}} with covers`);
  </script>
</body>

</html>
"""

    return html

def main():
    print("🎮 PC Games Grid Generator - OPTIMIZED for 16K+ games")
    print("=" * 60)
    
    games = load_games_data()
    if not games:
        return
    
    print("🔄 Generating optimized grid website with virtual scrolling...")
    html_content = generate_html(games)
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    file_size = os.path.getsize(OUTPUT_HTML) / (1024 * 1024)
    print(f"✅ Website generated: {OUTPUT_HTML} ({file_size:.2f} MB)")
    print(f"\n📊 Statistics:")
    print(f"   - Total games: {len(games)}")
    print(f"   - With covers: {sum(1 for g in games if g.get('cover_url') and g['cover_url'] != PLACEHOLDER_IMAGE)}")
    print(f"\n⚡ Performance optimizations:")
    print(f"   - Virtual scrolling (loads {ITEMS_PER_PAGE} games at a time)")
    print(f"   - Lazy loading images")
    print(f"   - Progressive rendering")
    print(f"   - Search doesn't require page reload")
    print(f"\n🔗 Each game has its own unique search URL!")

if __name__ == "__main__":
    main()