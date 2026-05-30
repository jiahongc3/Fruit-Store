export interface Fruit {
  fruit_id: string;
  name: string;
  category: string;
  price: number;
  unit: string;
  origin: string;
  stock: number;
  image_url: string;
}

export interface CartItem extends Fruit {
  quantity: number;
}

export interface CheckoutForm {
  name: string;
  phone: string;
  address: string;
  payment: string;
}