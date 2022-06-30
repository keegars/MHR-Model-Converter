namespace MHR_Model_Converter.Chain
{
    public static class ChainEnums
    {
        public enum ChainVersion
        {
            v35,
            v48
        }

        public enum ErrFlag
        {
            ErrFlags_None = 0,
            ErrFlags_Empty = 1,
            ErrFlags_NotFoundRefAsset = 2,
            ErrFlags_NotFoundIncludeAsset = 4
        }
    }
}