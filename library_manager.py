import streamlit as st
import pandas as pd
import json
import os
import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page config
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
.mainheader {
    font-size: 3rem !important;
    font-weight: 700;
    color: #4B0082;
    margin-bottom: 1rem;
    text-align: center;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}
.subheader {
    font-size: 1.8rem !important;
    font-weight: 700;
    color: #3B82F6;
    margin-top: 1rem;
    margin-bottom: 1rem;
}
.success-message {
    padding: 1rem;
    font-size: 1.5rem !important;
    font-weight: 700;
    background-color: #ECFDF5;
    border-radius: 0.375rem;
}
.error-message {
    padding: 1rem;
    background-color: #FEE3C7;
    border-left: 5px solid #E59E0B;
    border-radius: 0.375rem;
}
.book-card {
    background-color: #F3F4F6;
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
    transition: transform 0.3s ease;
}
.book-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
.read-badge,
.unread-badge {
    background-color: #10B981;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.875rem;
    font-weight: 600;
}
.stbutton > button {
    border-radius: 0.375rem;
}
</style>
""", unsafe_allow_html=True)

# Lottie loader function
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state
if 'library' not in st.session_state:
    st.session_state['library'] = []
if 'search_results' not in st.session_state:  # Fixed typo: search_ressults -> search_results
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'library'

def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
                return True
        else:
            st.session_state.library = []  # Reset to empty list if file doesn't exist
            return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        st.session_state.library = []  # Reset to empty list on error
        return False

def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
            return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

# Add a book to library
def add_book(title, author, publication_year, genre, read_status):
    # Convert read_status to boolean
    read_status_bool = True if read_status == "Read" else False
    book = {
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status_bool,  # Store as boolean
        'added_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

# Remove a book from library
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

# Search books
def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.library:
        if search_by == "Title" and search_term in book['title'].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book['author'].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book['genre'].lower():
            results.append(book)
    st.session_state.search_results = results

# Calculate library statistics
def calculate_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    percentage_read = (read_books / total_books) * 100 if total_books > 0 else 0
    genres = {}
    authors = {}
    decades = {}
    for book in st.session_state.library:
        # Count genres
        genres[book['genre']] = genres.get(book['genre'], 0) + 1
        # Count authors
        authors[book['author']] = authors.get(book['author'], 0) + 1
        # Count decades
        decade = (book['publication_year'] // 10) * 10  # Fixed decade calculation
        decades[decade] = decades.get(decade, 0) + 1

    # Sort by count
    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))
    return {
        'total_books': total_books,
        'read_books': read_books,
        'percentage_read': percentage_read,
        'genres': genres,
        'authors': authors,
        'decades': decades,
    }

def create_visualization(stats):
    if stats['total_books'] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=['Read', 'Unread'],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=0.4,
            textinfo='label+percent',
            marker=dict(colors=['#10B981', '#F87171'])
        )])
        fig_read_status.update_layout(
            title_text='Read vs Unread Books',
            showlegend=True,
            height=400,
        )
        st.plotly_chart(fig_read_status, use_container_width=True)

# Load the library
load_library()

# Sidebar
st.sidebar.markdown("<h1 style='text-align:center;'>📚 Library Menu</h1>", unsafe_allow_html=True)

# Lottie animation
lottie_book = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_4j7v1g5h.json")
if lottie_book:
    st_lottie(lottie_book, height=200, key='book_animation')

# Navigation
nav_options = st.sidebar.radio("Choose an option:", ["View Library", "Add Book", "Search Books", "Library Statistics"])
st.session_state.current_view = nav_options.lower().replace(" ", "_")

# Main Header
st.markdown("<h1 class='mainheader'> Personal Library Manager</h1>", unsafe_allow_html=True)

# Add Book View
if st.session_state.current_view == "add_book":
    st.markdown("<h2 class='subheader'>Add a New Book</h2>", unsafe_allow_html=True)
    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input("Publication Year", min_value=1900,
                                               max_value=datetime.datetime.now().year, step=1, value=2023)
        with col2:
            genre = st.selectbox("Genre", [
                "Fiction", "Non-Fiction", "Science Fiction", "Fantasy",
                "Mystery", "Biography", "History", "Art"
            ])
            read_status = st.radio("Read status", ["Read", "Unread"], horizontal=True)
            submit_button = st.form_submit_button(label="Add Book")

        if submit_button and title and author:
            add_book(title, author, publication_year, genre, read_status)
        if st.session_state.book_added:
            st.markdown("<div class='success-message'>Book added successfully!</div>", unsafe_allow_html=True)
            st.balloons()
            st.session_state.book_added = False

# Library View
elif st.session_state.current_view == "view_library":
    st.markdown("<h2 class='subheader'>Library</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.markdown("<div class='error-message'>Library empty! Please add some books.</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(4)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 4]:
                st.markdown(f"""
                    <div class='book-card'>
                        <h3>{book['title']}</h3>
                        <p><strong>Author:</strong> {book['author']}</p>
                        <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                        <p><strong>Genre:</strong> {book['genre']}</p>
                        <p><span class='{'read-badge' if book['read_status'] else 'unread-badge'}'>{
                            'Read' if book['read_status'] else 'Unread'}</span></p>
                    </div>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Remove", key=f"remove_{i}", use_container_width=True):
                        if remove_book(i):
                            st.experimental_rerun()
                with col2:
                    new_status = not book['read_status']
                    status_label = "Mark as read" if not book['read_status'] else "Mark as unread"
                    if st.button(status_label, key=f"status_{i}", use_container_width=True):
                        st.session_state.library[i]['read_status'] = new_status
                        save_library()
                        st.experimental_rerun()

    if st.session_state.book_removed:
        st.markdown("<div class='success-message'>Book removed successfully!</div>", unsafe_allow_html=True)
        st.session_state.book_removed = False

# Search View
elif st.session_state.current_view == "search_books":
    st.markdown("<h2 class='subheader'>Search Books</h2>", unsafe_allow_html=True)
    search_by = st.selectbox("Search by", ["Title", "Author", "Genre"])
    search_term = st.text_input("Enter search term:")
    if st.button("Search"):
        if search_term:
            with st.spinner("Searching..."):
                time.sleep(0.5)
                search_books(search_term, search_by)
    if hasattr(st.session_state, 'search_results') and st.session_state.search_results:
        st.markdown(f"<h3>Found {len(st.session_state.search_results)} result(s):</h3>", unsafe_allow_html=True)
        for book in st.session_state.search_results:
            st.markdown(f"""
                <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <p><span class='{'read-badge' if book['read_status'] else 'unread-badge'}'>{
                        'Read' if book['read_status'] else 'Unread'}</span></p>
                </div>
            """, unsafe_allow_html=True)
    elif 'search_term' in locals() and search_term:
        st.markdown("<div class='error-message'>No results found.</div>", unsafe_allow_html=True)

# Statistics View
elif st.session_state.current_view == "library_statistics":
    st.markdown("<h2 class='subheader'>Library Statistics</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.markdown("<div class='error-message'>Library empty! Please add some books.</div>", unsafe_allow_html=True)
    else:
        stats = calculate_library_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", stats['total_books'])
        with col2:
            st.metric("Read Books", stats['read_books'])
        with col3:
            st.metric("Percentage Read", f"{stats['percentage_read']:.1f}%")
        create_visualization(stats)
        if stats['authors']:
            st.markdown("<h3>Top Authors</h3>", unsafe_allow_html=True)
            top_authors = dict(list(stats['authors'].items())[:5])
            for author, count in top_authors.items():
                st.markdown(f"**{author}**: {count} book{'s' if count > 1 else ''}")

st.markdown("---")
st.markdown("Copyright © 2025 Rida Amir. Personal Library Manager.", unsafe_allow_html=True) 
