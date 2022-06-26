namespace MHR_Model_Converter.MDF
{
    public class BooleanHolder
    {
        public string Name { get; set; }

        public bool Selected { get; set; }

        public BooleanHolder(string name, bool selected)
        {
            Name = name;
            Selected = selected;
        }
    }
}