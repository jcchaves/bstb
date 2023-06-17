export interface PriceProps {
    min?: number,
    step: integer,
    value: number,
    onChange: (event: React.ChangeEvent<HTMLInputElement>) => void,
}