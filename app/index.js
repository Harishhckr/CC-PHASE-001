export const hello = () => "Hello from app";

export const greet = (name) => {
  if (!name) {
    return hello();
  }

  return `Hello, ${name}`;
};
