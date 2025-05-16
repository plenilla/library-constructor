'use client'; 

import { useRouter } from 'next/navigation';
import React from 'react';
import { MdArrowBack } from 'react-icons/md';

interface BackButtonProps {
  onClick?: () => void;
  className?: string;
  customAction?: () => void;
  name: string
}

const BackButton = ({ className = '', customAction, name }: BackButtonProps) => {
  const router = useRouter();
  const handleClick = () => {
    if (customAction){
        customAction();
    }else{
        router.back();
    }
  }
    return (
    <div className={`absolute top-0 text-3xl ${className}`}>
      <button
        onClick={handleClick}
        className="
          flex flex-row items-center 
          p-2 rounded-2xl pr-8
          hover:text-gray-500
          max-md:hover:text-inherit
          transition-colors duration-200
          select-none
        "
        aria-label="Назад"
      >
        <MdArrowBack className="mx-4 my-2" />
        {name}
      </button>
    </div>
  );
};

export default BackButton;