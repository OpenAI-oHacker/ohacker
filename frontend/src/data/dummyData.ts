
export const MOCK_USER = {
  id: 1,
  name: "Michał Pstrąg",
  avatar: "https://avatars.githubusercontent.com/u/47692610?v=4",
};

export const MOCK_USERS = [
  {
    name: "Alan Konarski",
    avatar: "https://sloppy-joe-app.imgix.net/blog_images/img-3064a-jpg-m9oR.jpg?usm=20&usmrad=15&w=512&h=512",
  }, {
    name: "Eryk Mazuś",
    avatar: "https://avatars.githubusercontent.com/u/21311210?v=4",
  }, {
    name: "Michał Pstrąg",
    avatar: "https://avatars.githubusercontent.com/u/47692610?v=4",
  }, 
];

export function getRandomUser() {
  // Calculate a random index between 0 and the array length - 1
  const randomIndex = Math.floor(Math.random() * MOCK_USERS.length);
  
  // Return the user at the random index
  return MOCK_USERS[randomIndex];
}

export const DUMMY_POSTS = [
  {
    id: 1,
    user: {
      name: "Jane Doe",
      avatar: "https://randomuser.me/api/portraits/women/68.jpg",
    },
    image:
      "https://images.unsplash.com/photo-1649972904349-6e44c42644a7?auto=format&fit=crop&w=500&q=80",
    caption: "Enjoying my coffee ☕️ in the morning sunshine!",
    comments: [
      {
        id: 11,
        user: {
          name: "Alex Smith",
          avatar: "https://randomuser.me/api/portraits/men/12.jpg",
        },
        text: "Looks delicious!",
      },
    ],
  },
  {
    id: 2,
    user: {
      name: "Alex Smith",
      avatar: "https://randomuser.me/api/portraits/men/12.jpg",
    },
    image:
      "https://images.unsplash.com/photo-1582562124811-c09040d0a901?auto=format&fit=crop&w=500&q=80",
    caption: "My cat being silly as always 😹",
    comments: [
      {
        id: 21,
        user: {
          name: "Jane Doe",
          avatar: "https://randomuser.me/api/portraits/women/68.jpg",
        },
        text: "So cute!!!",
      },
      {
        id: 22,
        user: {
          name: "Charlie",
          avatar: "https://randomuser.me/api/portraits/men/45.jpg",
        },
        text: "Give her a hug from me!",
      },
    ],
  },
];

