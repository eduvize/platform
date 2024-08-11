export interface ProfessionalDto {
    employers: EmploymentDto[];
}

export interface EmploymentDto {
    company_name: string;
    position: string;
    description: string;
    start_date: string | Date | null;
    end_date: string | Date | null;
    is_current: boolean;
    skills: string[];
}
