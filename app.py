
import requests
import pandas as pd
import streamlit as st

# ==================================================
# CONFIGURATION
# ==================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def get_books():
    """Fetch all books from the FastAPI backend."""
    try:
        response = requests.get(f"{API_URL}/books/", timeout=5)
        response.raise_for_status()

        data = response.json()

        if isinstance(data, list):
            return data

        st.error("Unexpected response received from the backend.")
        return []

    except requests.exceptions.ConnectionError:
        st.error(
            "Cannot connect to FastAPI. "
            "Start your backend and try again."
        )
        return []

    except requests.exceptions.RequestException as error:
        st.error(f"Error fetching books: {error}")
        return []


def add_book(title, author, isbn, quantity):
    """Add a new book."""
    data = {
        "title": title,
        "author": author,
        "isbn": isbn if isbn else None,
        "quantity": quantity
    }

    try:
        response = requests.post(
            f"{API_URL}/books/",
            json=data,
            timeout=5
        )

        if response.status_code in (200, 201):
            return True, "Book added successfully!"

        return False, f"Could not add book: {response.text}"

    except requests.exceptions.RequestException as error:
        return False, f"Backend connection error: {error}"


def update_book(book_id, title, author, isbn, quantity):
    """Update an existing book."""
    data = {
        "title": title,
        "author": author,
        "isbn": isbn if isbn else None,
        "quantity": quantity
    }

    try:
        response = requests.put(
            f"{API_URL}/books/{book_id}",
            json=data,
            timeout=5
        )

        if response.status_code == 200:
            return True, "Book updated successfully!"

        return False, f"Could not update book: {response.text}"

    except requests.exceptions.RequestException as error:
        return False, f"Backend connection error: {error}"


def delete_book(book_id):
    """Delete a book by ID."""
    try:
        response = requests.delete(
            f"{API_URL}/books/{book_id}",
            timeout=5
        )

        if response.status_code in (200, 204):
            return True, "Book deleted successfully!"

        return False, f"Could not delete book: {response.text}"

    except requests.exceptions.RequestException as error:
        return False, f"Backend connection error: {error}"


def show_books_table(books):
    """Display books in a table."""
    if not books:
        st.info("No books found.")
        return

    dataframe = pd.DataFrame(books)

    preferred_columns = [
        "id",
        "title",
        "author",
        "isbn",
        "quantity",
        "available"
    ]

    columns = [
        column for column in preferred_columns
        if column in dataframe.columns
    ]

    if columns:
        dataframe = dataframe[columns]

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True
    )


def get_book_options(books):
    """Create a readable selection list for books."""
    return {
        f'{book.get("title", "Untitled")} — ID {book["id"]}': book
        for book in books
        if book.get("id") is not None
    }


def search_books(books, keyword):
    """Search books by title, author, or ISBN."""
    keyword = keyword.strip().lower()

    if not keyword:
        return books

    return [
        book for book in books
        if keyword in str(book.get("title") or "").lower()
        or keyword in str(book.get("author") or "").lower()
        or keyword in str(book.get("isbn") or "").lower()
    ]


# ==================================================
# DARK THEME
# ==================================================

st.markdown("""
<style>
.stApp {
    background-color: #0b0f19;
    color: #ffffff;
}

[data-testid="stSidebar"] {
    background-color: #151b2b;
}

[data-testid="stHeader"] {
    background-color: #0b0f19;
}

h1, h2, h3, h4, p, label {
    color: #ffffff;
}

[data-testid="stMetric"] {
    background-color: #151b2b;
    border: 1px solid #273449;
    padding: 18px;
    border-radius: 12px;
}

.stButton > button {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 8px;
    min-height: 42px;
}

.stButton > button:hover {
    background-color: #1d4ed8;
    color: white;
    border: 1px solid #60a5fa;
}

[data-testid="stForm"] {
    background-color: #111827;
    border: 1px solid #273449;
    padding: 20px;
    border-radius: 12px;
}

[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div,
[data-baseweb="select"] > div {
    background-color: #1e293b;
    color: white;
}

[data-testid="stDataFrame"] {
    border: 1px solid #273449;
    border-radius: 8px;
}

hr {
    border-color: #374151;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

st.sidebar.title("📚 Library System")
st.sidebar.caption("Library Management Dashboard")
st.sidebar.divider()

page = st.sidebar.radio(
    "Choose a page",
    [
        "Dashboard",
        "Book Collection",
        "Add New Book",
        "Search Books",
        "Update Book",
        "Delete Book"
    ]
)

st.sidebar.divider()
st.sidebar.write("⚙️ Management")
st.sidebar.caption("Powered by Streamlit + FastAPI")


# ==================================================
# DASHBOARD
# ==================================================

if page == "Dashboard":

    st.title("📚 Library Dashboard")
    st.write("Welcome to your Library Management System.")

    books = get_books()

    total_titles = len(books)

    total_copies = sum(
        int(book.get("quantity") or 0)
        for book in books
    )

    available_titles = sum(
        1 for book in books
        if book.get(
            "available",
            int(book.get("quantity") or 0) > 0
        )
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="📖 Total Titles",
            value=total_titles
        )

    with col2:
        st.metric(
            label="📚 Total Copies",
            value=total_copies
        )

    with col3:
        st.metric(
            label="✅ Available Titles",
            value=available_titles
        )

    st.divider()

    st.subheader("📘 Book Collection Preview")

    if books:
        show_books_table(books[-5:][::-1])
    else:
        st.info("Your library is currently empty.")

    if st.button("🔄 Refresh Dashboard"):
        st.rerun()


# ==================================================
# BOOK COLLECTION
# ==================================================

elif page == "Book Collection":

    st.title("📚 Book Collection")
    st.write("View all books stored in your library database.")

    books = get_books()

    if books:

        keyword = st.text_input(
            "Search the collection",
            placeholder="Enter a title, author, or ISBN..."
        )

        filtered_books = search_books(books, keyword)

        st.write(f"**Books found:** {len(filtered_books)}")

        show_books_table(filtered_books)

    else:
        st.info("No books are currently registered.")


# ==================================================
# ADD NEW BOOK
# ==================================================

elif page == "Add New Book":

    st.title("➕ Add a New Book")
    st.write("Enter the book details to add it to your library.")

    with st.form("add_book_form", clear_on_submit=True):

        title = st.text_input(
            "Book Title",
            placeholder="Enter book title"
        )

        author = st.text_input(
            "Author",
            placeholder="Enter author name"
        )

        isbn = st.text_input(
            "ISBN (Optional)",
            placeholder="Enter ISBN"
        )

        quantity = st.number_input(
            "Quantity",
            min_value=0,
            value=1,
            step=1
        )

        submitted = st.form_submit_button(
            "➕ Add Book",
            use_container_width=True
        )

        if submitted:

            if not title.strip() or not author.strip():
                st.warning("Please enter both the book title and author.")

            else:
                success, message = add_book(
                    title.strip(),
                    author.strip(),
                    isbn.strip(),
                    int(quantity)
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


# ==================================================
# SEARCH BOOKS
# ==================================================

elif page == "Search Books":

    st.title("🔍 Search Books")
    st.write("Find books by title, author, or ISBN.")

    keyword = st.text_input(
        "Search keyword",
        placeholder="Start typing to search..."
    )

    if keyword.strip():

        books = get_books()
        results = search_books(books, keyword)

        st.subheader(f"Search Results: {len(results)}")

        if results:
            show_books_table(results)
        else:
            st.warning("No matching books were found.")

    else:
        st.info("Enter a keyword above to search for books.")


# ==================================================
# UPDATE BOOK
# ==================================================

elif page == "Update Book":

    st.title("✏️ Update Book Details")
    st.write("Select a book and edit its information.")

    books = get_books()

    if books:

        options = get_book_options(books)

        if options:

            selected_label = st.selectbox(
                "Select a book",
                list(options.keys())
            )

            selected_book = options[selected_label]

            st.divider()
            st.subheader("Edit Book Information")

            with st.form("update_book_form"):

                title = st.text_input(
                    "Book Title",
                    value=str(selected_book.get("title") or "")
                )

                author = st.text_input(
                    "Author",
                    value=str(selected_book.get("author") or "")
                )

                isbn = st.text_input(
                    "ISBN",
                    value=str(selected_book.get("isbn") or "")
                )

                quantity = st.number_input(
                    "Quantity",
                    min_value=0,
                    value=max(
                        0,
                        int(selected_book.get("quantity") or 0)
                    ),
                    step=1
                )

                submitted = st.form_submit_button(
                    "💾 Save Changes",
                    use_container_width=True
                )

                if submitted:

                    if not title.strip() or not author.strip():
                        st.warning("Title and author are required.")

                    else:
                        success, message = update_book(
                            selected_book["id"],
                            title.strip(),
                            author.strip(),
                            isbn.strip(),
                            int(quantity)
                        )

                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

        else:
            st.warning(
                "No book IDs were found. "
                "Check that your API returns an 'id' field."
            )

    else:
        st.info("There are no books available to update.")


# ==================================================
# DELETE BOOK
# ==================================================

elif page == "Delete Book":

    st.title("🗑️ Delete a Book")
    st.write("Select a book to remove it from the library.")

    books = get_books()

    if books:

        options = get_book_options(books)

        if options:

            selected_label = st.selectbox(
                "Select a book to delete",
                list(options.keys())
            )

            selected_book = options[selected_label]

            st.divider()

            st.subheader("Selected Book")

            st.write(f"**Title:** {selected_book.get('title', '')}")
            st.write(f"**Author:** {selected_book.get('author', '')}")
            st.write(f"**ISBN:** {selected_book.get('isbn') or 'N/A'}")
            st.write(f"**Quantity:** {selected_book.get('quantity', 0)}")

            st.warning(
                "Deleting a book will permanently remove it from the database."
            )

            confirm = st.checkbox(
                "I confirm that I want to delete this book."
            )

            if st.button(
                "🗑️ Delete Book",
                type="primary",
                disabled=not confirm,
                use_container_width=True
            ):

                success, message = delete_book(selected_book["id"])

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        else:
            st.warning(
                "No book IDs were found. "
                "Check that your API returns an 'id' field."
            )

    else:
        st.info("There are no books available to delete.")
