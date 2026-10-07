DROP TABLE if EXISTS meal_consumptions;
DROP TABLE if EXISTS purchases;
DROP TABLE if EXISTS ingredients;
DROP TABLE if EXISTS meals;
DROP TABLE if EXISTS inventory_items;
DROP TABLE if EXISTS products;
DROP TABLE if EXISTS ingredient_types;
DROP TABLE if EXISTS user_inventories;
DROP TABLE if EXISTS users;

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    postcode VARCHAR(10) NULL,
    daily_calorie_goal INT NULL CHECK (daily_calorie_goal > 0),
    spending_limit NUMERIC(10,2) NULL CHECK (spending_limit >= 0),
    budget_reset_at TIMESTAMP NULL
);

CREATE TABLE user_inventories (
    inventory_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE 
        REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE ingredient_types (
    ingredient_type_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) NULL UNIQUE,
    ingredient_type_id INT NULL
        REFERENCES ingredient_types(ingredient_type_id),
    name VARCHAR(255) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    currency CHAR(3) NOT NULL,
    brand VARCHAR(255) NULL,
    pack_size VARCHAR(50) NULL,
    unit_price NUMERIC(10,2) NULL,
    unit_currency CHAR(3) NULL,
    unit_name VARCHAR(10) NULL,
    supermarket VARCHAR(20) NOT NULL,
    last_price_update_at TIMESTAMP NOT NULL
);

CREATE TABLE inventory_items (
    inventory_item_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL
        REFERENCES products(product_id),
    inventory_id INT NOT NULL
        REFERENCES user_inventories(inventory_id) ON DELETE CASCADE,
    quantity NUMERIC(10,3) NOT NULL CHECK (quantity >= 0),
    quantity_unit VARCHAR(5) NOT NULL,

    UNIQUE (product_id, inventory_id)
);

CREATE TABLE meals (
    meal_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL
        REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    portion INT NOT NULL,
    portion_unit VARCHAR(20) NOT NULL,
    calories_per_serving NUMERIC(8,2) NULL CHECK (calories_per_serving >= 0)
);

CREATE TABLE ingredients (
    ingredient_id SERIAL PRIMARY KEY,
    meal_id INT NOT NULL
        REFERENCES meals(meal_id) ON DELETE CASCADE,
    ingredient_type_id INT NOT NULL
        REFERENCES ingredient_types(ingredient_type_id),
    quantity NUMERIC(10,3) NOT NULL,
    quantity_unit VARCHAR(20) NOT NULL
);

CREATE TABLE purchases (
    purchase_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL
        REFERENCES users(user_id) ON DELETE CASCADE,
    product_id INT NOT NULL
        REFERENCES products(product_id),
    quantity NUMERIC(10,3) NOT NULL CHECK (quantity > 0),
    quantity_unit VARCHAR(5) NOT NULL,
    price_paid NUMERIC(10,2) NOT NULL CHECK (price_paid >= 0),
    currency CHAR(3) NOT NULL,
    purchased_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE meal_consumptions (
    consumption_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL
        REFERENCES users(user_id) ON DELETE CASCADE,
    meal_id INT NULL
        REFERENCES meals(meal_id) ON DELETE SET NULL,
    meal_name VARCHAR(100) NOT NULL,
    servings NUMERIC(8,2) NOT NULL DEFAULT 1 CHECK (servings > 0),
    calories NUMERIC(10,2) NOT NULL CHECK (calories >= 0),
    consumed_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX purchases_user_time ON purchases(user_id, purchased_at);
CREATE INDEX meal_consumptions_user_time ON meal_consumptions(user_id, consumed_at);
