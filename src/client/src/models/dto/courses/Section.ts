import { ReactNode } from "react";

export interface Section {
    title: string;
    description: string;
    order: number;
    content: string | ReactNode;
}
