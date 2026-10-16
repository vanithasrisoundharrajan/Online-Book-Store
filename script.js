
const books = [
    {
        id: "1",
        title: "Learn Python",
        price: 499
    },
    {
        id: "2",
        title: "HTML and CSS Basics",
        price: 399
    },
    {
        id: "3",
        title: "JavaScript for Beginners",
        price: 599
    }
];

let cart = [];

const cartItems = document.getElementById("cart-items");
const cartCount = document.getElementById("cart-count");
const cartTotal = document.getElementById("cart-total");
const exploreButton = document.getElementById("explore-button");

exploreButton.addEventListener("click", function () {
    document.getElementById("books").scrollIntoView({
        behavior: "smooth"
    });
});

const addButtons = document.querySelectorAll(".add-to-cart");

addButtons.forEach(function (button) {
    button.addEventListener("click", function () {
        const bookId = button.dataset.id;

        const selectedBook = books.find(function (book) {
            return book.id === bookId;
        });

        if (selectedBook) {
            cart.push(selectedBook);
            updateCart();
        }
    });
});

function updateCart() {
    cartCount.textContent = cart.length;

    const total = cart.reduce(function (sum, book) {
        return sum + book.price;
    }, 0);

    cartTotal.textContent = total;

    if (cart.length === 0) {
        cartItems.innerHTML = "<p>Your cart is empty.</p>";
        return;
    }

    cartItems.innerHTML = cart.map(function (book, index) {
        return `
            <div class="cart-item">
                <span>${book.title} - ₹${book.price}</span>
                <button class="remove-button" data-index="${index}">
                    Remove
                </button>
            </div>
        `;
    }).join("");

    const removeButtons = cartItems.querySelectorAll(".remove-button");

    removeButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const index = Number(button.dataset.index);
            cart.splice(index, 1);
            updateCart();
        });
    });
}
