import * as React from "react";
import { cn } from "@/lib/utils";
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card";
import { X } from "lucide-react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl" | "full";
  className?: string;
  disableOutsideClick?: boolean;
  showCloseButton?: boolean;
}

const ModalContainer = ({ isOpen, onClose, title, children, actions, size, className, disableOutsideClick, showCloseButton }) => {
  React.useEffect(() => {
    const body = document.body;
    if (isOpen) {
      body.classList.add("overflow-hidden");
    } else {
      body.classList.remove("overflow-hidden");
    }
  }, [isOpen]);

  const sizeClasses = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    full: "max-w-full",
  };

  const handleOutsideClick = () => {
    if (!disableOutsideClick) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm transition-all"
      onClick={handleOutsideClick}
    >
      <Card
        className={cn(
          "relative mx-4 my-2 w-full overflow-hidden shadow-2xl",
          sizeClasses[size],
          className
        )}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Кнопка закрытия - теперь в абсолютном позиционировании поверх контента */}
        {showCloseButton && (
          <button
            onClick={onClose}
            className="fixed top-4 right-4 z-[100] text-muted-foreground hover:text-foreground rounded-full p-2 bg-background/80 backdrop-blur-sm opacity-80 transition-colors shadow-md hover:bg-background/100"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        )}

        {/* Header */}
        {title && (
          <CardHeader className="border-b p-4">
            <h3 className="text-lg font-semibold leading-none">
              {title}
            </h3>
          </CardHeader>
        )}

        {/* Content */}
        <CardContent className="p-0 md:p-6">{children}</CardContent>

        {/* Footer with Actions */}
        {actions && (
          <CardFooter className="border-t p-4">{actions}</CardFooter>
        )}
      </Card>
    </div>
  );
};

const Modal = React.forwardRef<HTMLDivElement, ModalProps>((props, ref) => {
  return <ModalContainer {...props} />;
});

Modal.displayName = "Modal";

export { Modal };
