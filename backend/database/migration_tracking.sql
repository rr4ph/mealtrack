ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_calorie_goal INT NULL CHECK (daily_calorie_goal > 0);
ALTER TABLE users ADD COLUMN IF NOT EXISTS spending_limit NUMERIC(10,2) NULL CHECK (spending_limit >= 0);
ALTER TABLE meals ADD COLUMN IF NOT EXISTS calories_per_serving NUMERIC(8,2) NULL CHECK (calories_per_serving >= 0);
CREATE TABLE IF NOT EXISTS purchases (
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

CREATE TABLE IF NOT EXISTS meal_consumptions (
    consumption_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL
        REFERENCES users(user_id) ON DELETE CASCADE,
    meal_id INT NULL
        REFERENCES meals(meal_id) ON DELETE SET NULL,
    meal_name VARCHAR(100) NOT NULL,
    calories NUMERIC(10,2) NOT NULL CHECK (calories >= 0),
    consumed_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS purchases_user_time ON purchases(user_id, purchased_at);
CREATE INDEX IF NOT EXISTS meal_consumptions_user_time ON meal_consumptions(user_id, consumed_at);
ALTER TABLE meal_consumptions ADD COLUMN IF NOT EXISTS servings NUMERIC(8,2) NOT NULL DEFAULT 1 CHECK (servings > 0);
ALTER TABLE users ADD COLUMN IF NOT EXISTS budget_reset_at TIMESTAMP NULL;
