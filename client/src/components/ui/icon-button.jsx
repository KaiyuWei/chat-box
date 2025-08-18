const IconButton = ({ 
  children, 
  onClick, 
  variant = "default", 
  size = "default", 
  className = "",
  ...props 
}) => {
  const baseClasses = "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50";
  
  const variants = {
    default: "bg-gray-200 text-gray-700 hover:bg-gray-300 hover:text-gray-800",
    ghost: "hover:bg-gray-100 hover:text-gray-900",
    outline: "border border-gray-200 bg-transparent hover:bg-gray-100",
  };
  
  const sizes = {
    default: "h-8 w-8",
    sm: "h-6 w-6",
    lg: "h-10 w-10",
  };
  
  const classes = `${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`;
  
  return (
    <button 
      className={classes}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
};

export default IconButton;
