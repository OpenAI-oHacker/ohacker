import { MOCK_USER } from "@/data/dummyData";
import { User } from "lucide-react";

interface NavbarProps {
  onNewPostClick: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onNewPostClick }) => (
  <nav className="bg-white/90 border-b border-gray-200 px-4 py-3 flex items-center justify-between sticky top-0 z-20 shadow-sm backdrop-blur-md">
    <div className="flex items-center">
      <span className="font-extrabold text-2xl tracking-tight text-neutral-800 select-none">
        Instagram
      </span>
    </div>
    <div className="flex items-center gap-5">
      <button
        onClick={onNewPostClick}
        className="bg-neutral-900 text-white px-4 py-2 rounded-lg hover:bg-neutral-100 hover:text-neutral-900 border border-gray-200 font-medium shadow transition"
      >
        + New Post
      </button>
      <div className="flex items-center gap-2">
        {MOCK_USER.avatar ? (
          <img
            src={MOCK_USER.avatar}
            alt={MOCK_USER.name}
            className="h-9 w-9 rounded-full border border-gray-200 object-cover shadow-sm"
          />
        ) : (
          <div className="bg-white border border-gray-200 h-9 w-9 rounded-full flex items-center justify-center">
            <User className="text-neutral-400" size={24} />
          </div>
        )}
        <span className="font-semibold text-neutral-800 hidden sm:block">
          {MOCK_USER.name}
        </span>
      </div>
    </div>
  </nav>
);
