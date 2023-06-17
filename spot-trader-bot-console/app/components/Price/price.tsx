import { PriceProps } from "@/app/types/components/price";

export default function Price({ value, step, min = 0, onChange }: PriceProps) {
    return (
        <input type="number" className="form-control" min={min} step={step} name="price" defaultValue={value} onChange={onChange} />
    );
}