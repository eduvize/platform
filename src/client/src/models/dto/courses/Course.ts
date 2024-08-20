import { Module } from "./Module";

export interface Course {
    title: string;
    description: string;

    modules: Module[];
}
