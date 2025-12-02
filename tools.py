"""
Agent Tools for Melissa Virtual Assistant

Contains the tools that the agent can use to help the user.
- Book tracking
- Web search (DuckDuckGo)

Note: AI Memory is now handled by memory_system.py (Mem0)
"""

import os
import logging
from typing import Annotated

logger = logging.getLogger(__name__)

# ============================================================
# BOOK DATABASE
# ============================================================

READ_BOOKS = {
    "book1": {
        "title": "Book 1",
        "author": "Author 1",
        "status": "read",
        "rating": None,
        "notes": ""
    },
    "book2": {
        "title": "Book 2", 
        "author": "Author 2",
        "status": "read",
        "rating": None,
        "notes": ""
    },
    "book3": {
        "title": "Book 3",
        "author": "Author 3", 
        "status": "read",
        "rating": None,
        "notes": ""
    }
}


# ============================================================
# BOOK TOOLS
# ============================================================

async def check_read_books() -> str:
    """
    Check and list all books that the user has read.
    """
    logger.info("Tool called: check_read_books")
    
    if not READ_BOOKS:
        return "You haven't recorded any books yet."
    
    books_list = []
    for book_id, book_info in READ_BOOKS.items():
        book_str = f"- {book_info['title']} by {book_info['author']}"
        if book_info.get('rating'):
            book_str += f" (Rating: {book_info['rating']}/5)"
        if book_info.get('notes'):
            book_str += f" - Notes: {book_info['notes']}"
        books_list.append(book_str)
    
    result = f"You have read {len(READ_BOOKS)} books:\n" + "\n".join(books_list)
    return result


async def get_book_details(
    book_name: Annotated[str, "The name or ID of the book to get details for"]
) -> str:
    """
    Get detailed information about a specific book.
    """
    logger.info(f"Tool called: get_book_details for '{book_name}'")
    
    book_name_lower = book_name.lower().strip()
    
    for book_id, book_info in READ_BOOKS.items():
        if book_id.lower() == book_name_lower or book_info['title'].lower() == book_name_lower:
            details = f"""
Book Details:
- Title: {book_info['title']}
- Author: {book_info['author']}
- Status: {book_info['status']}
- Rating: {book_info.get('rating', 'Not rated')}
- Notes: {book_info.get('notes', 'No notes')}
"""
            return details.strip()
    
    return f"I couldn't find a book called '{book_name}'. Available books are: {', '.join(b['title'] for b in READ_BOOKS.values())}"


# ============================================================
# WEB SEARCH (DuckDuckGo - no API key needed)
# ============================================================

async def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo.
    """
    logger.info(f"Tool called: web_search for '{query}'")
    
    try:
        from duckduckgo_search import DDGS
        
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "href": r.get("href", "")
                })
        
        if not results:
            return f"I couldn't find any results for '{query}'."
        
        formatted = f"Search results for '{query}':\n\n"
        for i, r in enumerate(results, 1):
            formatted += f"{i}. {r['title']}\n"
            formatted += f"   {r['body'][:200]}...\n\n"
        
        return formatted
        
    except ImportError:
        logger.warning("duckduckgo-search not installed")
        return "Web search unavailable. Please install duckduckgo-search."
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return f"Sorry, I couldn't search the web right now. Error: {str(e)}"
