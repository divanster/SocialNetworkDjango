declare module 'react-router-bootstrap' {
  import { ComponentType } from 'react';
  import { LinkProps } from 'react-router-dom';
  import { NavLinkProps } from 'react-router-dom';
  import { ButtonProps } from 'react-bootstrap';

  interface LinkContainerProps extends LinkProps {
    exact?: boolean;
    strict?: boolean;
    isActive?(match: any, location: any): boolean;
  }

  export const LinkContainer: ComponentType<LinkContainerProps>;

  interface ButtonLinkContainerProps extends ButtonProps {
    to: string;
  }

  export const ButtonLinkContainer: ComponentType<ButtonLinkContainerProps>;
}
