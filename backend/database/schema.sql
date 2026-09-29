CREATE TABLE users (
    user_id INT NOT NULL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    postcode VARCHAR(10) NULL
);

CREATE TABLE user_inventories (
    inventory_id INT NOT NULL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,

    FOREIGN KEY(user_id)
        REFERENCES users(user_id)
);

CREATE TABLE ingredient_types (
    ingredient_type_id INT NOT NULL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE products (
    product_id INT NOT NULL PRIMARY KEY,
    external_id VARCHAR(255) NULL UNIQUE,
    ingredient_type_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    currency CHAR(3) NOT NULL,
    brand VARCHAR(50) NULL,
    pack_size VARCHAR(50) NULL,
    unit_price NUMERIC(10,2) NULL,
    unit_currency CHAR(3) NULL,
    unit_name VARCHAR(10) NULL,
    supermarket VARCHAR(20) NOT NULL,
    last_price_update_at TIMESTAMP NOT NULL,

    FOREIGN KEY(ingredient_type_id)
        REFERENCES ingredient_types(ingredient_type_id)
);

CREATE TABLE inventory_items (
    inventory_item_id INT NOT NULL PRIMARY KEY,
    product_id INT NOT NULL,
    inventory_id INT NOT NULL,
    quantity NUMERIC(10,3) NOT NULL,
    quantity_unit VARCHAR(5) NOT NULL,

    FOREIGN KEY(product_id)
        REFERENCES products(product_id),

    FOREIGN KEY(inventory_id)
        REFERENCES user_inventories(inventory_id)
);

CREATE TABLE meals (
    meal_id INT NOT NULL PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    portion INT NOT NULL,
    portion_unit VARCHAR(20) NOT NULL,

    FOREIGN KEY(user_id)
        REFERENCES users(user_id)
);

CREATE TABLE ingredients (
    ingredient_id INT NOT NULL PRIMARY KEY,
    meal_id INT NOT NULL,
    ingredient_type_id INT NOT NULL,
    quantity NUMERIC(10,3) NOT NULL,
    quantity_unit VARCHAR(20) NOT NULL,

    FOREIGN KEY(meal_id)
        REFERENCES meals(meal_id),

    FOREIGN KEY(ingredient_type_id)
        REFERENCES ingredient_types(ingredient_type_id)
);


