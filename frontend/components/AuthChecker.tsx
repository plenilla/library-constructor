"use client"; // Убедитесь, что этот компонент является клиентским

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import useMyAxios from "@/composables/useMyAxios";
const AuthChecker = () => {
  const router = useRouter();
  const { request } = useMyAxios()
  useEffect(() => {
    
    const checkAuth = () => {
      const auth = localStorage.getItem("is_authenticated");
      if (auth === 'false' || !auth) {
      }
    };
   
    // Проверка аутентификации при монтировании компонента
    checkAuth();

    // Установка таймера на 20 минут (1200000 миллисекунд)
    const timer = setInterval(async () => {
      localStorage.setItem("is_authenticated", 'false');  
      await request("users/logout","GET")
      checkAuth();
    }, 12000000);

    // Очистка таймера при размонтировании компонента
    return () => clearInterval(timer);
  }, [router]);

  return null; // Этот компонент ничего не рендерит
};

export default AuthChecker;